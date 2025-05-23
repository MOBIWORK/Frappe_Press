# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

import frappe

from frappe import _
from enum import Enum
from press.utils import log_error, check_promotion_expire
from frappe.core.utils import find_all
from frappe.utils import getdate, cint, flt
from frappe.utils.data import fmt_money
from press.api.billing import get_stripe
from frappe.model.document import Document
from frappe.utils import rounded
from datetime import datetime, timedelta

from press.overrides import get_permission_query_conditions_for_doctype
from press.utils.billing import get_frappe_io_connection, convert_stripe_money

from press.press.doctype.team.team import (
    unsuspend_sites_when_recharge
)

class InvoiceDiscountType(Enum):
    FLAT_ON_TOTAL = "Flat On Total"


discount_type_string_to_enum = {
    "Flat On Total": InvoiceDiscountType.FLAT_ON_TOTAL}

DISCOUNT_MAP = {"Entry": 0, "Bronze": 0.05, "Silver": 0.1, "Gold": 0.15}


class Invoice(Document):
    def validate(self):
        self.validate_team()
        self.validate_dates()
        self.validate_duplicate()
        self.validate_items()
        self.calculate_values()
        self.compute_free_credits()

    def before_submit(self):
        if self.total > 0 and self.status != "Paid":
            frappe.throw("Invoice must be Paid to be submitted")
    
    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item.amount
        self.total = flt(total, 2)
    
    def calculate_discounts(self):
        self.total_discount_amount = sum([(item.discount or 0) for item in self.items]) + sum([(d.amount or 0) for d in self.discounts])
        # TODO: handle percent discount from discount table
        
        self.total_before_discount = self.total
        self.total_before_vat = self.total_before_discount - self.total_discount_amount
        self.total = flt(self.total_before_discount - self.total_discount_amount, 0)
    
    def calculate_amount_due(self):
        self.amount_due = flt(self.total - self.applied_credits, 0)
    
    def apply_taxes_if_applicable(self):
        if self.vat is None:
            vat_percentage = frappe.db.get_single_value(
                "Press Settings", "vat_percentage") or 0
            self.vat = vat_percentage
        amount_vat = rounded(self.total_before_vat * self.vat / 100, 2)
        self.total = rounded(self.total_before_vat + amount_vat)
        self.calculate_amount_due()
    
    def calculate_values(self):
        if self.status == "Paid" and self.docstatus == 1:
            # don't calculate if already invoice is paid and already submitted
            return
        self.calculate_total()
        self.calculate_discounts()
        self.apply_taxes_if_applicable()

    @frappe.whitelist()
    def finalize_invoice(self):
        if self.type == "Prepaid Credits":
            return

        self.calculate_values()
        
        if self.total == 0:
            self.status = "Empty"
            self.submit()
            return

        team = frappe.get_doc("Team", self.team)
        if not team.enabled:
            self.add_comment(
                "Info", "Skipping finalize invoice because team is disabled")
            return

        if self.partner_email and team.erpnext_partner:
            self.apply_partner_discount()

        # set as unpaid by default
        self.status = "Unpaid"
        self.update_item_descriptions()
        
        if self.amount_due > 0:
            self.apply_credit_balance()

        if self.amount_due == 0:
            self.status = "Paid"
            self.payment_date = datetime.now()

        if self.amount_due > 0:
            if self.payment_mode == "Prepaid Credits":
                self.payment_attempt_count += 1                
                self.add_comment(
                    "Comment",
                    "Not enough credits for this invoice.",
                )

        self.save()

        if self.status == "Paid":
            self.submit()
            self.unsuspend_sites_if_applicable()
            self.update_request_service_ai()
            validate_item_invoice(self.name)
            
    
    def unsuspend_sites_if_applicable(self):
        if (
            frappe.db.count(
                "Invoice",
                {
                    "status": "Unpaid",
                    "team": self.team,
                    "type": "Subscription",
                    "docstatus": ("<", 2),
                },
            )
            == 0
        ):
            # unsuspend sites only if all invoices are paid
            team = frappe.get_cached_doc("Team", self.team)
            team.unsuspend_sites(f"Invoice {self.name} Payment Successful.")
    
    def update_request_service_ai(self):
        # update service ai
        if self.period_start and self.period_end:
            date_obj = datetime.strptime(str(self.period_end), "%Y-%m-%d")
            new_date = date_obj + timedelta(days=1)
            start_time = str(self.period_start)
            end_time = new_date.strftime("%Y-%m-%d")
            
            frappe.db.sql(
                """
                UPDATE `tabRequest Service AI`
                SET status = 'Settled'
                WHERE start_time >= %s
                AND start_time < %s
                """,
                (start_time, end_time)
            )
    
    def on_submit(self):
        pass
        # self.create_invoice_on_frappeio()

    def on_update_after_submit(self):
        pass
        # self.create_invoice_on_frappeio()

    def after_insert(self):
        if self.get("amended_from"):
            values = {
                "modified": frappe.utils.now(),
                "modified_by": frappe.session.user,
                "new_invoice": self.name,
                "old_invoice": self.amended_from,
            }
            # link usage records of old cancelled invoice to the new amended invoice
            frappe.db.sql(
                """
                UPDATE
                    `tabUsage Record`
                SET
                    `invoice` = %(new_invoice)s,
                    `modified` = %(modified)s,
                    `modified_by` = %(modified_by)s
                WHERE
                    `invoice` = %(old_invoice)s
                """,
                values=values,
            )

    def create_stripe_invoice(self):
        if self.payment_mode != "Card":
            return

        stripe = get_stripe()

        if self.type == "Prepaid Credits":
            return

        if self.status == "Paid":
            # void an existing invoice if payment was done via credits
            if self.stripe_invoice_id:
                stripe.Invoice.void_invoice(self.stripe_invoice_id)
                self.add_comment(
                    text=(
                        f"Stripe Invoice {self.stripe_invoice_id} voided because"
                        " payment is done via credits."
                    )
                )
            return

        if self.stripe_invoice_id:
            invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
            stripe_invoice_total = convert_stripe_money(invoice.total)
            if self.amount_due == stripe_invoice_total:
                # return if an invoice with the same amount is already created
                return
            else:
                # if the amount is changed, void the stripe invoice and create a new one
                stripe.Invoice.void_invoice(self.stripe_invoice_id)
                formatted_amount = fmt_money(
                    stripe_invoice_total, currency=self.currency)
                self.add_comment(
                    text=(
                        f"Stripe Invoice {self.stripe_invoice_id} of amount {formatted_amount} voided."
                    )
                )
                self.stripe_invoice_id = ""
                self.stripe_invoice_url = ""

        if self.amount_due <= 0:
            return

        customer_id = frappe.db.get_value(
            "Team", self.team, "stripe_customer_id")
        amount = int(self.amount_due * 100)
        stripe.InvoiceItem.create(
            customer=customer_id,
            description=self.get_stripe_invoice_item_description(),
            amount=amount,
            currency=self.currency.lower(),
            idempotency_key=f"invoiceitem:{self.name}:{amount}",
        )
        invoice = stripe.Invoice.create(
            customer=customer_id,
            collection_method="charge_automatically",
            auto_advance=True,
            idempotency_key=f"invoice:{self.name}:{amount}",
        )
        self.stripe_invoice_id = invoice["id"]
        self.status = "Invoice Created"
        self.save()

    def find_stripe_invoice(self):
        stripe = get_stripe()
        invoices = stripe.Invoice.list(
            customer=frappe.db.get_value(
                "Team", self.team, "stripe_customer_id")
        )
        description = self.get_stripe_invoice_item_description()
        for invoice in invoices.data:
            if invoice.lines.data[0].description == description and invoice.status != "void":
                return invoice["id"]

    def get_stripe_invoice_item_description(self):
        start = getdate(self.period_start)
        end = getdate(self.period_end)
        period_string = f"{start.strftime('%b %d')} - {end.strftime('%b %d')} {end.year}"
        return f"Frappe Cloud Subscription ({period_string})"

    @frappe.whitelist()
    def finalize_stripe_invoice(self):
        stripe = get_stripe()
        stripe.Invoice.finalize_invoice(self.stripe_invoice_id)

    def validate_duplicate(self):
        if self.type != "Subscription":
            return

        if self.period_start and self.period_end and self.is_new():
            query = (
                f"select `name` from `tabInvoice` where team = '{self.team}' and"
                f" status = 'Draft' and ('{self.period_start}' between `period_start` and"
                f" `period_end` or '{self.period_end}' between `period_start` and"
                " `period_end`)"
            )

            intersecting_invoices = [x[0]
                                     for x in frappe.db.sql(query, as_list=True)]

            if intersecting_invoices:
                frappe.throw(
                    f"There are invoices with intersecting periods:{', '.join(intersecting_invoices)}",
                    frappe.DuplicateEntryError,
                )

    def validate_team(self):
        team = frappe.get_cached_doc("Team", self.team)

        self.customer_name = team.billing_name or frappe.utils.get_fullname(
            self.team)
        self.customer_email = (
            frappe.db.get_value(
                "Communication Email", {
                    "parent": team.user, "type": "invoices"}, ["value"]
            )
            or team.user
        )
        self.currency = team.currency
        if not self.payment_mode:
            self.payment_mode = team.payment_mode
        if not self.currency:
            frappe.throw(
                f"Cannot create Invoice because Currency is not set in Team {self.team}"
            )

        # To prevent copying of team level discounts again
        self.remove_previous_team_discounts()

        for invoice_discount in team.discounts:
            self.append(
                "discounts",
                {
                    "discount_type": invoice_discount.discount_type,
                    "based_on": invoice_discount.based_on,
                    "percent": invoice_discount.percent,
                    "amount": invoice_discount.amount,
                    "via_team": True,
                },
            )

    def remove_previous_team_discounts(self):
        team_discounts = find_all(self.discounts, lambda x: x.via_team)

        for discount in team_discounts:
            self.remove(discount)

    def validate_dates(self):
        if not self.period_start:
            return
        if not self.period_end:
            period_start = getdate(self.period_start)
            # period ends on last day of month
            self.period_end = frappe.utils.get_last_day(period_start)

        # due date
        self.due_date = self.period_end

    def update_item_descriptions(self):
        for item in self.items:
            if not item.description and item.document_type == "Site" and item.plan:
                site_name = item.document_name.split(".archived")[0]
                plan = frappe.get_cached_value("Plan", item.plan, "plan_title")
                how_many_days = f"{cint(item.quantity)} day{'s' if item.quantity > 1 else ''}"
                item.description = f"{site_name} active for {how_many_days} on {plan} plan"

    def add_usage_record(self, usage_record):
        if self.type != "Subscription":
            return
        # return if this usage_record is already accounted for in an invoice
        if usage_record.invoice:
            return

        # return if this usage_record does not fall inside period of invoice
        usage_record_date = getdate(usage_record.date)
        start = getdate(self.period_start)
        end = getdate(self.period_end)
        if not (start <= usage_record_date <= end):
            return

        invoice_item = self.get_invoice_item_for_usage_record(usage_record)
        # if not found, create a new invoice item
        if not invoice_item:
            invoice_item = self.append(
                "items",
                {
                    "document_type": usage_record.document_type,
                    "document_name": usage_record.document_name,
                    "plan": usage_record.plan,
                    "quantity": 0,
                    "rate": usage_record.amount,
                    "site": usage_record.site,
                },
            )

        invoice_item.quantity = (invoice_item.quantity or 0) + 1

        if usage_record.payout:
            self.payout += usage_record.payout

        self.add_discount_if_available()
        self.save()
        usage_record.db_set("invoice", self.name)

    def remove_usage_record(self, usage_record):
        if self.type != "Subscription":
            return
        # return if invoice is not in draft mode
        if self.docstatus != 0:
            return

        # return if this usage_record is of a different invoice
        if usage_record.invoice != self.name:
            return

        invoice_item = self.get_invoice_item_for_usage_record(usage_record)
        if not invoice_item:
            return

        if invoice_item.quantity <= 0:
            return

        invoice_item.quantity -= 1
        self.save()
        usage_record.db_set("invoice", None)

    def get_invoice_item_for_usage_record(self, usage_record):
        invoice_item = None
        for row in self.items:
            conditions = (
                row.document_type == usage_record.document_type
                and row.document_name == usage_record.document_name
                and row.plan == usage_record.plan
                and row.rate == usage_record.amount
            )
            if row.document_type == "Marketplace App":
                conditions = conditions and row.site == usage_record.site
            if conditions:
                invoice_item = row
        return invoice_item

    def validate_items(self):
        items_to_remove = []
        for row in self.items:
            if row.quantity == 0:
                items_to_remove.append(row)
            else:
                row.amount = rounded(row.quantity * row.rate, 2)

        for item in items_to_remove:
            self.remove(item)

    def compute_free_credits(self):
        self.free_credits = sum(
            [d.amount for d in self.credit_allocations if d.source == "Free Credits"]
        )

    def apply_partner_discount(self):
        if self.flags.on_partner_conversion:
            return

        # check if discount is already added
        if self.discounts:
            return

        discount_note = (
            "Flat Partner Discount"
            if self.payment_mode == "Partner Credits"
            else "New Partner Discount"
        )

        partner_level, legacy_contract = self.get_partner_level()
        # give 10% discount for partners
        discount_percent = 0.1 if legacy_contract == 1 else DISCOUNT_MAP.get(
            partner_level)

        total_partner_discount = 0
        for item in self.items:
            if item.document_type in ("Site", "Server", "Database Server"):
                item.discount = item.amount * discount_percent
                total_partner_discount += item.discount

        if total_partner_discount > 0:
            self.append(
                "discounts",
                {
                    "discount_type": "Flat On Total",
                    "based_on": "Amount",
                    "percent": discount_percent,
                    "amount": total_partner_discount,
                    "note": discount_note,
                    "via_team": False,
                },
            )

        self.save()
        self.reload()

    def get_partner_level(self):
        # fetch partner level from frappe.io
        client = self.get_frappeio_connection()
        response = client.session.get(
            f"{client.url}/api/method/get_partner_level",
            headers=client.headers,
            params={"email": self.partner_email},
        )

        if response.ok:
            res = response.json()
            partner_level = res.get("message")
            legacy_contract = res.get("legacy_contract")
            if partner_level:
                return partner_level, legacy_contract
        else:
            self.add_comment(
                text="Failed to fetch partner level" + "<br><br>" + response.text)

    def set_total_and_discount(self):
        total_discount_amount = 0

        for invoice_discount in self.discounts:
            discount_type = discount_type_string_to_enum[invoice_discount.discount_type]
            if discount_type == InvoiceDiscountType.FLAT_ON_TOTAL:
                total_discount_amount += self.get_flat_on_total_discount_amount(
                    invoice_discount)

        self.total_discount_amount = total_discount_amount
        self.total_before_vat = self.total_before_discount - total_discount_amount

    def set_total_and_vat(self):
        if self.vat is None:
            vat_percentage = frappe.db.get_single_value(
                "Press Settings", "vat_percentage") or 0
            self.vat = vat_percentage
        amount_vat = rounded(self.total_before_vat * self.vat / 100, 2)
        self.total = rounded(self.total_before_vat + amount_vat)

    def get_flat_on_total_discount_amount(self, invoice_discount):
        discount_amount = 0

        if invoice_discount.based_on == "Amount":
            if invoice_discount.amount > self.total_before_discount:
                frappe.throw(
                    f"Discount amount {invoice_discount.amount} cannot be"
                    f" greater than total amount {self.total_before_discount}"
                )

            discount_amount = invoice_discount.amount
        elif invoice_discount.based_on == "Percent":
            if invoice_discount.percent > 100:
                frappe.throw(
                    f"Discount percentage {invoice_discount.percent} cannot be greater than 100%"
                )
            discount_amount = self.total_before_discount * \
                (invoice_discount.percent / 100)

        return discount_amount

    def on_cancel(self):
        # make reverse entries for credit allocations
        for transaction in self.credit_allocations:
            doc = frappe.get_doc(
                doctype="Balance Transaction",
                team=self.team,
                type="Adjustment",
                source=transaction.source,
                currency=transaction.currency,
                amount=transaction.amount,
                amount_promotion_1=transaction.amount_promotion_1,
                amount_promotion_2=transaction.amount_promotion_2,
                description=f"Reversed on cancel of Invoice {self.name}",
            )
            doc.insert()
            doc.submit()

    def apply_partner_credits(self):
        client = self.get_frappeio_connection()
        response = client.session.post(
            f"{client.url}/api/method/consume_credits_against_fc_invoice",
            headers=client.headers,
            data={"invoice": self.as_json()},
        )

        if response.ok:
            res = response.json()
            partner_order = res.get("message")

            if partner_order:
                self.frappe_partner_order = partner_order
                self.amount_paid = self.amount_due
                self.status = "Paid"
                self.save()
                self.submit()
        else:
            self.add_comment(
                text="Failed to pay via Partner credits" + "<br><br>" + response.text
            )

    def add_discount_if_available(self, allow_save=False):
        self.validate_items()
        self.calculate_values()
        
        today = frappe.utils.today()
        team = frappe.get_cached_doc("Team", self.team)
        total_allocated_1 = 0
        total_allocated_2 = 0
        
        # so tien chua co VAT
        total_before_vat = self.total_before_vat
        
        # lay sanh sach trans để giao dịch cho km1
        unallocated_balances = frappe.db.get_all(
			"Balance Transaction",
			filters={
				"team": self.team,
				"type": "Adjustment",
				"unallocated_amount_1": (">", 0),
				"docstatus": ("<", 2),
                "date_promotion_1": (">", today),
			},
			fields=["name", "unallocated_amount_1", "promotion1_amount_used", "source", "(COALESCE(unallocated_amount_1, 0) - COALESCE(promotion1_amount_used, 0)) AS remaining_amount"],
			order_by="date_promotion_1 desc, creation desc",
		)
        # sort by ascending for FIFO
        unallocated_balances.reverse()
        
        # ap dung km1
        for balance in unallocated_balances:
            if total_before_vat == 0:
                break
            # so tien km1 tra duoc
            allocated_promotion_1 = balance.remaining_amount or 0
            if allocated_promotion_1 > 0:
                allocated_promotion_1 = min(total_before_vat, allocated_promotion_1)
                total_before_vat -= allocated_promotion_1

                doc = frappe.get_doc("Balance Transaction", balance.name)
                doc.promotion1_amount_used = (doc.promotion1_amount_used or 0) + allocated_promotion_1
                doc.save()
                total_allocated_1 += allocated_promotion_1

        # lay sanh sach trans để giao dịch cho km2        
        unallocated_balances = frappe.db.get_all(
			"Balance Transaction",
			filters={
				"team": self.team,
				"type": "Adjustment",
				"unallocated_amount_2": (">", 0),
				"docstatus": ("<", 2),
			},
            fields=["name", "unallocated_amount_2", "promotion2_amount_used", "source", "(COALESCE(unallocated_amount_2, 0) - COALESCE(promotion2_amount_used, 0)) AS remaining_amount"],
			order_by="creation desc",
		)
        # sort by ascending for FIFO
        unallocated_balances.reverse()
        
        # ap dung km2
        for balance in unallocated_balances:
            if total_before_vat == 0:
                break
            # so tien km2 tra duoc
            allocated_promotion_2 = balance.remaining_amount or 0
            if allocated_promotion_2>0:
                allocated_promotion_2 = min(total_before_vat, allocated_promotion_2)
                total_before_vat -= allocated_promotion_2

                doc = frappe.get_doc("Balance Transaction", balance.name)
                doc.promotion2_amount_used = (doc.promotion2_amount_used or 0) + allocated_promotion_2
                doc.save()
                total_allocated_2 += allocated_promotion_2
        
        # them km vao discount
        tien_km_ap_dung = total_allocated_1 + total_allocated_2
        if tien_km_ap_dung > 0:
            if len(self.discounts) and self.discounts[0].based_on == "Amount":
                doc_discount = self.discounts[0]
                doc_discount.amount = doc_discount.amount + tien_km_ap_dung
            else:
                self.append(
                    "discounts",
                    {
                        "discount_type": "Flat On Total",
                        "based_on": "Amount",
                        "amount": tien_km_ap_dung,
                        "note": "Tien khuyen mai",
                    },
                )
        # save invoice
        if allow_save:
            self.save()
    
    def apply_balance_of_expenses(self, total_allocated=0, total_allocated_1=0, total_allocated_2=0):
        # tru so tien sau khi chi tra hoa don
        balance_transaction = frappe.get_doc(
            doctype="Balance Transaction",
            team=self.team,
            type="Applied To Invoice",
            amount=total_allocated * -1,
            amount_promotion_1=total_allocated_1 * -1,
            amount_promotion_2=total_allocated_2 * -1,
            invoice=self.name,
        ).insert()
        balance_transaction.submit()

        self.applied_credits = sum(row.amount for row in self.credit_allocations)
        # tinh toan lai so tien
        self.calculate_values()

    
    def apply_credit_balance(self):
        balance_all = frappe.get_cached_doc("Team", self.team).get_balance_all()
        if balance_all <= 0:
            return

        total_allocated = 0
        total_allocated_1 = 0
        total_allocated_2 = 0
        tien_km1_ap_dung = 0
        tien_km2_ap_dung = 0
        
        # so tien chua co VAT
        total_before_vat = self.total_before_vat
        
        # lay sanh sach trans để giao dịch cho km1
        unallocated_balances = frappe.db.get_all(
			"Balance Transaction",
			filters={
				"team": self.team,
				"type": "Adjustment",
				"docstatus": ("<", 2)
			},
            or_filters={
                "unallocated_amount_1": (">", 0),
                "promotion1_amount_used": (">", 0)
            },
			fields=["name", "unallocated_amount_1", "promotion1_amount_used", "source", "(COALESCE(unallocated_amount_1, 0) - COALESCE(promotion1_amount_used, 0)) AS remaining_amount"],
			order_by="date_promotion_1 desc, creation desc",
		)
        # sort by ascending for FIFO
        unallocated_balances.reverse()
        
        # ap dung km1
        for balance in unallocated_balances:
            if total_before_vat == 0:
                break
            
            # kiem tra km1 con han khong
            promotion_expire = check_promotion_expire(balance.name)
            # so tien con lai cua km1 ap dung duoc
            if promotion_expire:
                allocated_promotion_1 = balance.promotion1_amount_used or 0
            else:
                allocated_promotion_1 = min(total_before_vat, balance.remaining_amount)
                total_before_vat -= allocated_promotion_1
                
            if allocated_promotion_1 > 0:
                tat_ca_tien_km1_ap_dung = balance.promotion1_amount_used
                if not promotion_expire:
                    total_allocated_1 += allocated_promotion_1 + balance.promotion1_amount_used
                    tien_km1_ap_dung += allocated_promotion_1
                    tat_ca_tien_km1_ap_dung = total_allocated_1
                    
                self.append(
                    "credit_allocations",
                    {
                        "transaction": balance.name,
                        "amount": 0,
                        "amount_promotion_1": tat_ca_tien_km1_ap_dung,
                        "amount_promotion_2": 0,
                        "currency": self.currency,
                        "source": balance.source,
                    },
                )
                doc = frappe.get_doc("Balance Transaction", balance.name)
                if not promotion_expire:
                    doc.append(
                        "allocated_to",
                        {
                            "invoice": self.name,
                            "amount": 0,
                            "amount_promotion_1": tat_ca_tien_km1_ap_dung,
                            "amount_promotion_2": 0,
                            "currency": self.currency
                        },
                    )
                doc.promotion1_amount_used = 0
                doc.save()

        # lay sanh sach trans để giao dịch cho km2        
        unallocated_balances = frappe.db.get_all(
			"Balance Transaction",
			filters={
				"team": self.team,
				"type": "Adjustment",
				"docstatus": ("<", 2),
                "unallocated_amount_2": (">", 0),
			},
			fields=["name", "unallocated_amount_2", "source", "promotion2_amount_used", "(COALESCE(unallocated_amount_2, 0) - COALESCE(promotion2_amount_used, 0)) AS remaining_amount"],
			order_by="creation desc",
		)
        # sort by ascending for FIFO
        unallocated_balances.reverse()

        # ap dung km2
        for balance in unallocated_balances:
            if total_before_vat == 0:
                break
            # so tien con lai cua km2 ap dung duoc
            allocated_promotion_2 = balance.remaining_amount
            if allocated_promotion_2>0:
                allocated_promotion_2 = min(total_before_vat, allocated_promotion_2)
                total_before_vat -= allocated_promotion_2

                tien_km2_ap_dung += allocated_promotion_2
                tat_ca_tien_km2_ap_dung = allocated_promotion_2 + balance.promotion2_amount_used
                total_allocated_2 += tat_ca_tien_km2_ap_dung
                
                self.append(
                    "credit_allocations",
                    {
                        "transaction": balance.name,
                        "amount": 0,
                        "amount_promotion_1": 0,
                        "amount_promotion_2": tat_ca_tien_km2_ap_dung,
                        "currency": self.currency,
                        "source": balance.source,
                    },
                )
                doc = frappe.get_doc("Balance Transaction", balance.name)
                doc.append(
                    "allocated_to",
                    {
                        "invoice": self.name,
                        "amount": 0,
                        "amount_promotion_1": 0,
                        "amount_promotion_2": tat_ca_tien_km2_ap_dung,
                        "currency": self.currency
                    },
                )
                doc.promotion2_amount_used = 0
                doc.save()
        
        # them km vao discount
        tien_km_ap_dung = tien_km1_ap_dung + tien_km2_ap_dung
        if tien_km_ap_dung > 0:
            if len(self.discounts) and self.discounts[0].based_on == "Amount":
                doc_discount = self.discounts[0]
                doc_discount.amount = doc_discount.amount + tien_km_ap_dung
            else:
                self.append(
                    "discounts",
                    {
                        "discount_type": "Flat On Total",
                        "based_on": "Amount",
                        "amount": tien_km_ap_dung,
                        "note": "Tien khuyen mai",
                    },
                )

            # tinh toan lai so tien khi ap dung km
            self.calculate_values()
        
        # tien con phai tra cho hoa don
        due = self.amount_due
        
        # lay sanh sach trans để giao dịch cho tien nap
        unallocated_balances = frappe.db.get_all(
			"Balance Transaction",
			filters={
				"team": self.team,
				"type": "Adjustment",
				"unallocated_amount": (">", 0),
				"docstatus": ("<", 2),
			},
			fields=["name", "unallocated_amount", "source"],
			order_by="creation desc",
		)
        # sort by ascending for FIFO
        unallocated_balances.reverse()
        
        # ap dung so tien goc
        for balance in unallocated_balances:
            if due == 0:
                break
            # so tien goc tra duoc
            allocated_root = balance.unallocated_amount or 0
            if allocated_root>0:
                allocated_root = min(due, allocated_root)
                due -= allocated_root

                self.append(
                    "credit_allocations",
                    {
                        "transaction": balance.name,
                        "amount": allocated_root,
                        "amount_promotion_1": 0,
                        "amount_promotion_2": 0,
                        "currency": self.currency,
                        "source": balance.source,
                    },
                )
                doc = frappe.get_doc("Balance Transaction", balance.name)
                doc.append(
                    "allocated_to",
                    {
                        "invoice": self.name,
                        "amount": allocated_root,
                        "amount_promotion_1": 0,
                        "amount_promotion_2": 0,
                        "currency": self.currency
                    },
                )
                doc.save()
                total_allocated += allocated_root
        
        self.apply_balance_of_expenses(total_allocated, total_allocated_1, total_allocated_2)


    def create_next(self):
        # the next invoice's period starts after this invoice ends
        next_start = frappe.utils.add_days(self.period_end, 1)

        already_exists = frappe.db.exists(
            "Invoice",
            {
                "team": self.team,
                "period_start": next_start,
                "type": "Subscription",
            },  # Adding type 'Subscription' to ensure no other type messes with this
        )

        if not already_exists:
            return frappe.get_doc(
                doctype="Invoice", team=self.team, period_start=next_start
            ).insert()

    def get_pdf(self):
        print_format = self.meta.default_print_format
        return frappe.utils.get_url(
            f"/api/method/frappe.utils.print_format.download_pdf?doctype=Invoice&name={self.name}&format={print_format}&no_letterhead=0"
        )

    @frappe.whitelist()
    def create_invoice_on_frappeio(self):
        if self.flags.skip_frappe_invoice:
            return
        if self.status != "Paid":
            return
        if self.amount_paid == 0:
            return
        if self.frappe_invoice or self.frappe_partner_order:
            return

        try:
            team = frappe.get_doc("Team", self.team)
            address = (
                frappe.get_doc(
                    "Address", team.billing_address) if team.billing_address else None
            )
            client = self.get_frappeio_connection()
            response = client.session.post(
                f"{client.url}/api/method/create-fc-invoice",
                headers=client.headers,
                data={
                    "team": team.as_json(),
                    "address": address.as_json(),
                    "invoice": self.as_json(),
                },
            )
            if response.ok:
                res = response.json()
                invoice = res.get("message")

                if invoice:
                    self.frappe_invoice = invoice
                    self.fetch_invoice_pdf()
                    self.save()
                    return invoice
            else:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")
                self.add_comment(
                    text="Failed to create invoice on frappe.io" +
                    "<br><br>" + str(soup.find("pre"))
                )

                log_error(
                    "Frappe.io Invoice Creation Error",
                    data={"invoice": self.name,
                          "frappe_io_response": response.text},
                )
        except Exception:
            traceback = "<pre><code>" + frappe.get_traceback() + "</pre></code>"
            self.add_comment(
                text="Failed to create invoice on frappe.io" + "<br><br>" + traceback
            )

            log_error(
                "Frappe.io Invoice Creation Error",
                data={"invoice": self.name, "traceback": traceback},
            )

    @frappe.whitelist()
    def fetch_invoice_pdf(self):
        if self.frappe_invoice:
            client = self.get_frappeio_connection()
            url = (
                client.url + "/api/method/frappe.utils.print_format.download_pdf?"
                f"doctype=Sales%20Invoice&name={self.frappe_invoice}&"
                "format=Frappe%20Cloud&no_letterhead=0"
            )

            with client.session.get(url, headers=client.headers, stream=True) as r:
                r.raise_for_status()
                ret = frappe.get_doc(
                    {
                        "doctype": "File",
                        "attached_to_doctype": "Invoice",
                        "attached_to_name": self.name,
                        "attached_to_field": "invoice_pdf",
                        "folder": "Home/Attachments",
                        "file_name": self.frappe_invoice + ".pdf",
                        "is_private": 1,
                        "content": r.content,
                    }
                )
                ret.save(ignore_permissions=True)
                self.invoice_pdf = ret.file_url

    def get_frappeio_connection(self):
        if not hasattr(self, "frappeio_connection"):
            self.frappeio_connection = get_frappe_io_connection()

        return self.frappeio_connection

    def update_transaction_details(self, stripe_charge=None):
        if not stripe_charge:
            return
        stripe = get_stripe()
        charge = stripe.Charge.retrieve(stripe_charge)
        if charge.balance_transaction:
            balance_transaction = stripe.BalanceTransaction.retrieve(
                charge.balance_transaction)
            self.exchange_rate = balance_transaction.exchange_rate
            self.transaction_amount = convert_stripe_money(
                balance_transaction.amount)
            self.transaction_net = convert_stripe_money(
                balance_transaction.net)
            self.transaction_fee = convert_stripe_money(
                balance_transaction.fee)
            self.transaction_fee_details = []
            for row in balance_transaction.fee_details:
                self.append(
                    "transaction_fee_details",
                    {
                        "description": row.description,
                        "amount": convert_stripe_money(row.amount),
                        "currency": row.currency.upper(),
                    },
                )
            self.save()
            return True

    def update_razorpay_transaction_details(self, payment):
        self.transaction_amount = convert_stripe_money(payment["amount"])
        self.transaction_net = convert_stripe_money(
            payment["amount"] - payment["fee"])
        self.transaction_fee = convert_stripe_money(payment["fee"])

        charges = [
            {
                "description": "GST",
                "amount": convert_stripe_money(payment["tax"]),
                "currency": payment["currency"],
            },
            {
                "description": "Razorpay Fee",
                "amount": convert_stripe_money(payment["fee"] - payment["tax"]),
                "currency": payment["currency"],
            },
        ]

        for row in charges:
            self.append(
                "transaction_fee_details",
                {
                    "description": row["description"],
                    "amount": row["amount"],
                    "currency": row["currency"].upper(),
                },
            )

        self.save()

    @frappe.whitelist()
    def refund(self, reason):
        stripe = get_stripe()
        charge = None
        if self.type in ["Subscription", "Service"]:
            stripe_invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
            charge = stripe_invoice.charge
        elif self.type == "Prepaid Credits":
            payment_intent = stripe.PaymentIntent.retrieve(
                self.stripe_payment_intent_id)
            charge = payment_intent["charges"]["data"][0]["id"]

        if not charge:
            frappe.throw(
                "Cannot refund payment because Stripe Charge not found for this invoice"
            )

        stripe.Refund.create(charge=charge)
        self.status = "Refunded"
        self.save()
        self.add_comment(text=f"Refund reason: {reason}")

    def consume_credits_and_mark_as_paid(self, reason=None):
        if self.amount_due <= 0:
            frappe.throw("Amount due is less than or equal to 0")

        team = frappe.get_doc("Team", self.team)
        available_credits = team.get_balance_all()
        if available_credits < self.amount_due:
            available = frappe.utils.fmt_money(
                available_credits, 2, self.currency)
            frappe.throw(
                f"Available credits ({available}) is less than amount due"
                f" ({self.get_formatted('amount_due')})"
            )

        remark = "Manually consuming credits and marking the unpaid invoice as paid."
        if reason:
            remark += f" Reason: {reason}"

        self.change_stripe_invoice_status("Paid")

        # negative value to reduce balance by amount
        amount = self.amount_due * -1
        balance_transaction = team.allocate_credit_amount(
            amount, source="", remark=f"{remark}, Ref: Invoice {self.name}"
        )

        self.add_comment(
            text=(
                "Manually consuming credits and marking the unpaid invoice as paid."
                f" {frappe.utils.get_link_to_form('Balance Transaction', balance_transaction.name)}"
            )
        )
        self.db_set("status", "Paid")

    @frappe.whitelist()
    def change_stripe_invoice_status(self, status):
        stripe = get_stripe()
        if status == "Paid":
            stripe.Invoice.modify(self.stripe_invoice_id, paid=True)
        elif status == "Uncollectible":
            stripe.Invoice.mark_uncollectible(self.stripe_invoice_id)
        elif status == "Void":
            stripe.Invoice.void_invoice(self.stripe_invoice_id)

    @frappe.whitelist()
    def refresh_stripe_payment_link(self):
        stripe = get_stripe()
        stripe_invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
        self.stripe_invoice_url = stripe_invoice.hosted_invoice_url
        self.save()

        # Also send back the updated payment link
        return self.stripe_invoice_url


def finalize_draft_invoices():
    """
    - Runs every hour
    - Processes 500 invoices at a time
    - Finalizes the invoices whose
    - period ends today and time is 6PM or later
    - period has ended before
    """

    today = frappe.utils.today()
    # only finalize for enabled teams
    # since 'limit' returns the same set of invoices for disabled teams which are ignored
    enabled_teams = frappe.get_all("Team", {"enabled": 1}, pluck="name")

    # get draft invoices whose period has ended or ends today
    invoices = frappe.db.get_all(
        "Invoice",
        filters={
            "status": "Draft",
            "type": "Subscription",
            "period_end": ("<=", today),
            "team": ("in", enabled_teams),
        },
        pluck="name",
        limit=500,
        order_by="total desc",
    )

    current_time = frappe.utils.get_datetime().time()
    today = frappe.utils.getdate()
    for name in invoices:
        invoice = frappe.get_doc("Invoice", name)
        # don't finalize if invoice ends today and time is before 6 PM
        if invoice.period_end == today and current_time.hour < 18:
            continue
        finalize_draft_invoice(invoice)


def finalize_unpaid_prepaid_credit_invoices():
    """Should be run daily in contrast to `finalize_draft_invoices`, which runs hourly"""
    today = frappe.utils.today()

    # Invoices with `Prepaid Credits` or `Partner Credits` as mode and unpaid
    invoices = frappe.db.get_all(
        "Invoice",
        filters={
            "status": "Unpaid",
            "type": "Subscription",
            "period_end": ("<=", today),
            "payment_mode": "Prepaid Credits",
        },
        pluck="name",
    )

    current_time = frappe.utils.get_datetime().time()
    today = frappe.utils.getdate()
    for name in invoices:
        invoice = frappe.get_doc("Invoice", name)
        # don't finalize if invoice ends today and time is before 6 PM
        if invoice.period_end == today and current_time.hour < 18:
            continue
        finalize_draft_invoice(invoice)


def finalize_draft_invoice(invoice):
    if isinstance(invoice, str):
        invoice = frappe.get_doc("Invoice", invoice)

    try:
        invoice.finalize_invoice()
    except Exception:
        frappe.db.rollback()
        msg = "<pre><code>" + frappe.get_traceback() + "</pre></code>"
        invoice.add_comment(text="Finalize Invoice Failed" + "<br><br>" + msg)
    finally:
        frappe.db.commit()  # For the comment

    try:
        invoice.create_next()
    except Exception:
        frappe.db.rollback()
        log_error("Invoice creation for next month failed",
                  invoice=invoice.name)


get_permission_query_conditions = get_permission_query_conditions_for_doctype(
    "Invoice")


def calculate_gst(amount):
    return amount * 0.18


def validate_item_invoice(invoice_name):
    items = frappe.get_all("Invoice Item", 
        filters={
            "parent": invoice_name
        },
        fields=["name", "item_code", "item_name", "document_type", "document_name", "site", "plan"]
    )

    for item in items:
        data_update = {}
        if item.document_type == "Site":
            doc = frappe.db.get_value("Plan", item.plan, ['service_id', 'item_description', 'en_item_description'], as_dict=1)
            if doc:
                if not item.item_code:
                    data_update['item_code'] = doc.service_id
                if not item.item_name:
                    data_update['item_name'] = doc.item_description
        elif item.document_type == "Marketplace App":
            doc = frappe.db.get_value("Marketplace App", item.document_name, ['service_id', 'item_description', 'en_item_description'], as_dict=1)
            if doc:
                if not item.item_code:
                    data_update['item_code'] = doc.service_id
                if not item.item_name:
                    data_update['item_name'] = doc.item_description
        if data_update:
            frappe.db.set_value('Invoice Item', item.name, data_update)
            frappe.db.commit()