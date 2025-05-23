# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

import os
import frappe

from frappe import _
from frappe.core.utils import find
from typing import List
from hashlib import blake2b
from frappe.utils import get_fullname
from frappe.utils import get_url_to_form, random_string
from press.utils import (
    log_error,
    get_current_team,
    get_date_expire_promotion
)
from press.telegram_utils import Telegram
from frappe.model.document import Document
from press.exceptions import FrappeioServerNotSet
from frappe.contacts.address_and_contact import load_address_and_contact
from press.press.doctype.account_request.account_request import AccountRequest
from press.utils.billing import (
    get_erpnext_com_connection,
    get_frappe_io_connection,
    get_stripe,
    process_micro_debit_test_charge,
)
from press.utils.telemetry import capture
from datetime import datetime, timedelta

class Team(Document):
    whitelisted_methods = [
        "enabled",
        "team_title",
        "user",
        "partner_email",
        "billing_team",
        "team_members",
        "child_team_members",
        "notify_email",
        "country",
        "currency",
        "payment_mode",
        "default_payment_method",
    ]

    def get_doc(self, doc):
        user = frappe.db.get_value(
            "User",
            self.user,
            ["first_name", "phone", "user_image", "user_type"],
            as_dict=True,
        )
        doc.balance = self.get_balance_all()
        doc.user = user
        doc.is_desk_user = user.user_type == "System User"
        return doc

    def onload(self):
        load_address_and_contact(self)

    def validate(self):
        self.validate_duplicate_members()
        self.set_team_currency()
        self.set_team_payment_mode()
        self.set_default_user()
        self.set_billing_name()
        self.set_partner_email()

    def before_insert(self):
        if not self.notify_email:
            self.notify_email = self.user

        if not self.referrer_id:
            self.set_referrer_id()

    def set_referrer_id(self):
        h = blake2b(digest_size=4)
        h.update(self.user.encode())
        self.referrer_id = h.hexdigest()

    def set_partner_email(self):
        if self.erpnext_partner and not self.partner_email:
            self.partner_email = self.user

    def delete(self, force=False, workflow=False):
        if force:
            return super().delete()

        if workflow:
            return frappe.get_doc(
                {"doctype": "Team Deletion Request", "team": self.name}
            ).insert()

        frappe.throw(
            f"You are only deleting the Team Document for {self.name}. To continue to"
            " do so, pass force=True with this call. Else, pass workflow=True to raise"
            " a Team Deletion Request to trigger complete team deletion process."
        )

    def disable_account(self):
        self.suspend_sites("Account disabled")
        self.enabled = False
        self.save()
        self.add_comment("Info", "disabled account")

    def enable_account(self):
        self.unsuspend_sites("Account enabled")
        self.enabled = True
        self.save()
        self.add_comment("Info", "enabled account")

    @classmethod
    def create_new(
            cls,
            account_request: AccountRequest,
            first_name: str,
            phone: str,
            password: str = None,
            country: str = None,
            is_us_eu: bool = False,
            via_erpnext: bool = False,
            user_exists: bool = False,
    ):
        """Create new team along with user (user created first)."""
        team = frappe.get_doc(
            {
                "doctype": "Team",
                "user": account_request.email,
                "country": country,
                "enabled": 1,
                "via_erpnext": via_erpnext,
                "is_us_eu": is_us_eu,
                "account_request": account_request.name,
            }
        )

        if not user_exists:
            user = team.create_user(
                first_name, phone, account_request.email, password, account_request.role
            )
        else:
            user = frappe.get_doc("User", account_request.email)
            user.append_roles(account_request.role)
            user.save(ignore_permissions=True)

        team.team_title = "Parent Team"
        team.insert(ignore_permissions=True, ignore_links=True)
        team.append("team_members", {"user": user.name})
        if not account_request.invited_by_parent_team:
            team.append("communication_emails", {
                        "type": "invoices", "value": user.name})
            team.append(
                "communication_emails", {
                    "type": "marketplace_notifications", "value": user.name}
            )
        else:
            team.parent_team = account_request.invited_by

        if account_request.saas_product:
            team.is_saas_user = 1

        team.save(ignore_permissions=True)

        # team.create_stripe_customer()

        if account_request.referrer_id:
            team.create_referral_bonus(account_request.referrer_id)

        if not team.via_erpnext:
            if not account_request.invited_by_parent_team:
                team.create_upcoming_invoice()
            # TODO: Partner account moved to PRM
            if team.has_partner_account_on_erpnext_com():
                team.enable_erpnext_partner_privileges()

        return team

    @staticmethod
    def create_user(first_name=None, phone=None, email=None, password=None, role=None):
        user = frappe.new_doc("User")
        user.first_name = first_name
        user.phone = phone
        user.email = email
        user.owner = email
        user.new_password = password
        user.append_roles(role)
        user.flags.no_welcome_mail = True
        user.save(ignore_permissions=True)
        return user

    def create_user_for_member(
            self, first_name=None, phone=None, email=None, password=None, role=None
    ):
        user = frappe.db.get_value("User", email, ["name"], as_dict=True)
        if not user:
            user = self.create_user(
                first_name, phone, email, password, role)

        self.append("team_members", {"user": user.name})
        self.save(ignore_permissions=True)

    def remove_team_member(self, member):
        member_to_remove = find(self.team_members, lambda x: x.user == member)
        if member_to_remove:
            self.remove(member_to_remove)
        else:
            frappe.throw(f"Team member {frappe.bold(member)} does not exists")

        self.save(ignore_permissions=True)

    def set_billing_name(self):
        if not self.billing_name:
            self.billing_name = frappe.utils.get_fullname(self.user)

    def set_default_user(self):
        if not self.user and self.team_members:
            self.user = self.team_members[0].user

    def set_team_currency(self):
        if not self.currency and self.country:
            # self.currency = "INR" if self.country == "India" else "USD"
            self.currency = "VND"

    def set_team_payment_mode(self):
        if not self.payment_mode:
            self.payment_mode = "Prepaid Credits"

    def get_user_list(self):
        return [row.user for row in self.team_members]

    def get_users_only_in_this_team(self):
        return [
            user
            for user in self.get_user_list()
            if not frappe.db.exists("Team Member", {"user": user, "parent": ("!=", self.name)})
        ]

    def validate_duplicate_members(self):
        team_users = self.get_user_list()
        duplicate_members = [m for m in team_users if team_users.count(m) > 1]
        duplicate_members = list(set(duplicate_members))
        if duplicate_members:
            frappe.throw(
                _("Duplicate Team Members: {0}").format(
                    ", ".join(duplicate_members)),
                frappe.DuplicateEntryError,
            )

    def validate_payment_mode(self):
        if not self.payment_mode and self.get_balance_all() > 0:
            self.payment_mode = "Prepaid Credits"

        if self.has_value_changed("payment_mode"):
            if self.payment_mode == "Card":
                if frappe.db.count("Stripe Payment Method", {"team": self.name}) == 0:
                    frappe.throw("No card added")
            if self.payment_mode == "Prepaid Credits":
                if self.get_balance_all() < 0:
                    frappe.throw("Tài khoản không đủ số dư")

        if not self.is_new() and not self.default_payment_method:
            # if default payment method is unset
            # then set the is_default field for Stripe Payment Method to 0
            payment_methods = frappe.db.get_list(
                "Stripe Payment Method", {"team": self.name, "is_default": 1}
            )
            for pm in payment_methods:
                doc = frappe.get_doc("Stripe Payment Method", pm.name)
                doc.is_default = 0
                doc.save()

    def on_update(self):
        self.validate_payment_mode()
        self.update_draft_invoice_payment_mode()
        self.validate_partnership_date()

# if not self.is_new() and self.billing_name and not frappe.conf.allow_tests:
# if self.has_value_changed("billing_name"):
# self.update_billing_details_on_frappeio()

    def validate_partnership_date(self):
        if self.erpnext_partner or not self.partnership_date:
            return

        if partner_email := self.partner_email:
            frappe_partnership_date = frappe.db.get_value(
                "Team",
                {"enabled": 1, "erpnext_partner": 1,
                 "partner_email": partner_email},
                "frappe_partnership_date",
            )
            if frappe_partnership_date and frappe_partnership_date > self.partnership_date:
                frappe.throw(
                    "Partnership date cannot be less than the partnership date of the partner"
                )

    def update_draft_invoice_payment_mode(self):
        if self.has_value_changed("payment_mode"):
            draft_invoices = frappe.get_all(
                "Invoice", filters={"docstatus": 0, "team": self.name}, pluck="name"
            )

            for invoice in draft_invoices:
                frappe.db.set_value("Invoice", invoice,
                                    "payment_mode", self.payment_mode)

    @frappe.whitelist()
    def impersonate(self, member, reason):
        user = frappe.db.get_value("Team Member", member, "user")
        impersonation = frappe.get_doc(
            {
                "doctype": "Team Member Impersonation",
                "user": user,
                "impersonator": frappe.session.user,
                "team": self.name,
                "member": member,
                "reason": reason,
            }
        )
        impersonation.save()
        frappe.local.login_manager.login_as(user)

    @frappe.whitelist()
    def enable_erpnext_partner_privileges(self):
        self.erpnext_partner = 1
        self.partner_email = self.user
        self.frappe_partnership_date = self.get_partnership_start_date()
        self.servers_enabled = 1
        self.save(ignore_permissions=True)
        self.create_partner_referral_code()
        self.create_new_invoice()

    @frappe.whitelist()
    def disable_erpnext_partner_privileges(self):
        self.erpnext_partner = 0
        self.servers_enabled = 0
        self.save(ignore_permissions=True)

    def create_partner_referral_code(self):
        if not self.partner_referral_code:
            self.partner_referral_code = random_string(10)
            self.save(ignore_permissions=True)

    def get_partnership_start_date(self):
        if frappe.flags.in_test:
            return frappe.utils.getdate()

        client = get_frappe_io_connection()
        data = client.get_value(
            "Partner", "start_date", {
                "email": self.partner_email, "enabled": 1}
        )
        if not data:
            frappe.throw("Partner not found on frappe.io")
        start_date = frappe.utils.getdate(data.get("start_date"))
        return start_date

    def create_new_invoice(self):
        """
        After enabling partner privileges, new invoice should be created
        to track the partner achivements
        """
        # check if any active user with an invoice
        if not frappe.get_all(
                "Invoice", {"team": self.name, "docstatus": ("<", 2)}, pluck="name"
        ):
            return
        today = frappe.utils.getdate()
        current_invoice = frappe.db.get_value(
            "Invoice",
            {
                "team": self.name,
                "type": "Subscription",
                "docstatus": 0,
                "period_end": frappe.utils.get_last_day(today),
            },
            "name",
        )

        if not current_invoice:
            return

        current_inv_doc = frappe.get_doc("Invoice", current_invoice)

        if (
                current_inv_doc.partner_email and current_inv_doc.partner_email == self.partner_email
        ):
            # don't create new invoice if partner email is set
            return

        if (
                not current_invoice
                or today == frappe.utils.get_last_day(today)
                or today == current_inv_doc.period_start
        ):
            # don't create invoice if new team or today is the last day of the month
            return
        else:
            current_inv_doc.period_end = frappe.utils.add_days(today, -1)
            current_inv_doc.flags.on_partner_conversion = True
            current_inv_doc.save()
            current_inv_doc.finalize_invoice()

        # create invoice
        invoice = frappe.get_doc(
            {
                "doctype": "Invoice",
                "team": self.name,
                "type": "Subscription",
                "period_start": today,
            }
        )
        invoice.insert()

    def allocate_free_credits(self):
        # if self.via_erpnext or self.is_saas_user:
        #     # dont allocate free credits for signups via erpnext
        #     # since they get a 14 day free trial site
        #     return

        if not self.free_credits_allocated:
            # allocate free credits on signup
            # credits_field = "free_credits_vnd" if self.currency == "VND" else "free_credits_usd"
            credits_field = "free_credits_vnd"
            credit_amount = frappe.db.get_single_value(
                "Press Settings", credits_field)
            if not credit_amount:
                return
            self.allocate_free_credit_amount(
                credit_amount, source="Free Credits")
            self.free_credits_allocated = 1
            self.save()
            self.reload()

    def create_referral_bonus(self, referrer_id):
        # Get team name with this this referrer id
        referrer_team = frappe.db.get_value(
            "Team", {"referrer_id": referrer_id})
        frappe.get_doc(
            {"doctype": "Referral Bonus", "for_team": self.name,
                "referred_by": referrer_team}
        ).insert(ignore_permissions=True)

    def has_member(self, user):
        return user in self.get_user_list()

    def is_defaulter(self):
        if self.free_account:
            return False

        try:
            unpaid_invoices = frappe.get_all(
                "Invoice",
                {
                    "status": "Unpaid",
                    "team": self.name,
                    "docstatus": ("<", 2),
                    "type": "Subscription",
                },
                pluck="name",
            )
        except frappe.DoesNotExistError:
            return False

        return unpaid_invoices

    def create_stripe_customer(self):
        if not self.stripe_customer_id:
            stripe = get_stripe()
            customer = stripe.Customer.create(
                email=self.user, name=get_fullname(self.user))
            self.stripe_customer_id = customer.id
            self.save()

    def update_billing_details(self, billing_details):
        if self.billing_address:
            address_doc = frappe.get_doc("Address", self.billing_address)
        else:
            address_doc = frappe.new_doc("Address")
            address_doc.address_title = billing_details.billing_name or self.billing_name
            address_doc.append(
                "links",
                {
                    "link_doctype": self.doctype,
                    "link_name": self.name,
                    "link_title": self.name
                },
            )

        data_update = {
            "company_name": billing_details.company_name,
            "address_line1": billing_details.address,
            "areas_of_concern": billing_details.areas_of_concern,
            "state": billing_details.state,
            "city": billing_details.state,
            "county": billing_details.county,
            "enterprise": billing_details.enterprise,
            "email_id": billing_details.email_id,
            "phone": billing_details.phone,
            "tax_code": billing_details.tax_code,
            "pincode": billing_details.postal_code,
            "country": billing_details.country,
            "gstin": billing_details.gstin,
        }

        if billing_details.number_of_employees or billing_details.number_of_employees == 0:
            data_update['number_of_employees'] = billing_details.number_of_employees

        address_doc.update(data_update)
        address_doc.flags.ignore_mandatory = True
        address_doc.save()
        address_doc.reload()

        self.billing_name = billing_details.billing_name or self.billing_name
        self.billing_address = address_doc.name
        self.save()
        self.reload()

        # self.update_billing_details_on_stripe(address_doc)
        # self.update_billing_details_on_frappeio()
        self.update_billing_details_on_draft_invoices()

    def update_billing_details_survey(self, billing_details):
        if self.billing_address:
            address_doc = frappe.get_doc("Address", self.billing_address)
        else:
            address_doc = frappe.new_doc("Address")
            address_doc.address_title = billing_details.billing_name or self.billing_name
            address_doc.append(
                "links",
                {
                    "link_doctype": self.doctype,
                    "link_name": self.name,
                    "link_title": self.name
                },
            )

        data_update = {
            "areas_of_concern": billing_details.areas_of_concern,
            "concerns_feature": billing_details.concerns_feature
        }

        if billing_details.number_of_employees or billing_details.number_of_employees == 0:
            data_update['number_of_employees'] = billing_details.number_of_employees

        address_doc.update(data_update)
        address_doc.flags.ignore_mandatory = True
        address_doc.save()
        address_doc.reload()

        self.billing_name = billing_details.billing_name or self.billing_name
        self.billing_address = address_doc.name
        self.save()
        self.reload()

        # self.update_billing_details_on_stripe(address_doc)
        # self.update_billing_details_on_frappeio()
        self.update_billing_details_on_draft_invoices()

    def update_billing_details_on_draft_invoices(self):
        draft_invoices = frappe.get_all(
            "Invoice", {"team": self.name, "docstatus": 0}, pluck="name"
        )
        for draft_invoice in draft_invoices:
            # Invoice.customer_name set by Invoice.validate()
            frappe.get_doc("Invoice", draft_invoice).save()

    def update_billing_details_on_frappeio(self):
        if frappe.flags.in_install:
            return

        try:
            frappeio_client = get_frappe_io_connection()
        except FrappeioServerNotSet as e:
            if frappe.conf.developer_mode or os.environ.get("CI"):
                return
            else:
                raise e

        previous_version = self.get_doc_before_save()

        if not previous_version:
            self.load_doc_before_save()
            previous_version = self.get_doc_before_save()

        previous_billing_name = previous_version.billing_name

        if previous_billing_name and previous_billing_name != self.billing_name:
            try:
                frappeio_client.rename_doc(
                    "Customer", previous_billing_name, self.billing_name)
                frappe.msgprint(
                    f"Renamed customer from {previous_billing_name} to {self.billing_name}"
                )
            except Exception:
                log_error(
                    "Failed to rename customer on frappe.io", traceback=frappe.get_traceback()
                )

    def update_billing_details_on_stripe(self, address=None):
        stripe = get_stripe()
        if not address:
            address = frappe.get_doc("Address", self.billing_address)

        country_code = frappe.db.get_value("Country", address.country, "code")
        stripe.Customer.modify(
            self.stripe_customer_id,
            address={
                "line1": address.address_line1,
                "postal_code": address.pincode,
                "county": address.county,
                "state": address.state,
                "country": country_code.upper(),
            },
        )

    def create_payment_method(self, payment_method_id, set_default=False):
        # stripe = get_stripe()
        # payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

        # doc = frappe.get_doc(
        #     {
        #         "doctype": "Stripe Payment Method",
        #         "stripe_payment_method_id": payment_method["id"],
        #         "last_4": payment_method["card"]["last4"],
        #         "name_on_card": payment_method["billing_details"]["name"],
        #         "expiry_month": payment_method["card"]["exp_month"],
        #         "expiry_year": payment_method["card"]["exp_year"],
        #         "brand": payment_method["card"]["brand"] or "",
        #         "team": self.name,
        #     }
        # )
        # doc.insert()

        # unsuspend sites on payment method added
        self.unsuspend_sites(reason="Payment method added")
        if set_default:
            # doc.set_default()
            self.reload()

        # allocate credits if not already allocated
        self.allocate_free_credits()
        # Telemetry: Added card
        capture("added_card_or_prepaid_credits",
                "fc_signup", self.account_request)

        # return doc

    def get_payment_methods(self):
        return frappe.db.get_all(
            "Stripe Payment Method",
            {"team": self.name},
            [
                "name",
                "last_4",
                "name_on_card",
                "expiry_month",
                "expiry_year",
                "brand",
                "is_default",
                "creation",
            ],
            order_by="creation desc",
        )

    def get_past_invoices(self):
        invoices = frappe.db.get_all(
            "Invoice",
            filters={
                "team": self.name,
                "status": ("not in", ("Draft", "Refunded")),
                "docstatus": ("!=", 2),
            },
            fields=[
                "name",
                "total",
                "amount_due",
                "status",
                "type",
                "stripe_invoice_url",
                "period_start",
                "period_end",
                "due_date",
                "payment_date",
                "currency",
                "invoice_pdf",
                "due_date as date"
            ],
            order_by="due_date desc",
        )

        for invoice in invoices:
            invoice.formatted_total = frappe.utils.fmt_money(
                invoice.total, 2, invoice.currency)
            invoice.stripe_link_expired = False
            if invoice.status == "Unpaid":
                days_diff = frappe.utils.date_diff(
                    frappe.utils.now(), invoice.due_date)
                if days_diff > 30:
                    invoice.stripe_link_expired = True
        return invoices

    def allocate_credit_amount(self, amount, source, remark=None):
        doc = frappe.get_doc(
            doctype="Balance Transaction",
            team=self.name,
            type="Adjustment",
            source=source,
            amount=amount,
            description=remark,
        )
        doc.insert(ignore_permissions=True)
        doc.submit()
        # change payment mode to prepaid credits if default is card or not set
        self.payment_mode = (
            "Prepaid Credits" if self.payment_mode != "Partner Credits" else self.payment_mode
        )
        self.save()
        return doc

    def allocate_free_credit_amount(self, amount, source, remark=None):
        # date_promotion_1 = frappe.utils.now_datetime().strftime('%Y-%m-%d')
        # date_promotion_1 = datetime.strptime(date_promotion_1, '%Y-%m-%d')
        doc = frappe.get_doc(
            doctype="Balance Transaction",
            team=self.name,
            type="Adjustment",
            source=source,
            amount_promotion_2=amount,
            # amount_promotion_1=amount,
            # date_promotion_1=date_promotion_1,
            description=remark,
        )
        doc.insert(ignore_permissions=True)
        doc.submit()
        # change payment mode to prepaid credits if default is card or not set
        self.payment_mode = (
            "Prepaid Credits" if self.payment_mode != "Partner Credits" else self.payment_mode
        )
        self.save()
        return doc

    def allocate_referral_bonus_credit_amount(self, amount, source, remark=None):
        doc = frappe.get_doc(
            doctype="Balance Transaction",
            team=self.name,
            type="Adjustment",
            source=source,
            amount_promotion_2=amount,
            description=remark,
        )
        doc.insert(ignore_permissions=True)
        doc.submit()
        # change payment mode to prepaid credits if default is card or not set
        self.payment_mode = (
            "Prepaid Credits" if self.payment_mode != "Partner Credits" else self.payment_mode
        )
        self.save()
        return doc

    def get_available_credits(self):
        def get_stripe_balance():
            return self.get_stripe_balance()

        return frappe.cache().hget(
            "customer_available_credits", self.name, generator=get_stripe_balance
        )

    def get_stripe_balance(self):
        stripe = get_stripe()
        customer_object = stripe.Customer.retrieve(self.stripe_customer_id)
        balance = (customer_object["balance"] * -1) / 100
        return balance

    @frappe.whitelist()
    def get_balance(self):
        res = frappe.db.get_all(
            "Balance Transaction",
            filters={"team": self.name, "docstatus": 1},
            order_by="creation desc",
            limit=1,
            pluck="ending_balance",
        )
        if not res:
            return 0
        return res[0]

    @frappe.whitelist()
    def get_balance_all(self):
        res = frappe.db.get_all(
            "Balance Transaction",
            fields=['ending_balance', 'promotion_balance_1',
                    'promotion_balance_2'],
            filters={"team": self.name, "docstatus": 1},
            order_by="creation desc",
            limit=1,
        )
        balance_promotion = frappe.get_all(
            "Balance Transaction",
            filters={"docstatus": 1, "team": self.name},
            or_filters={
                "promotion1_amount_used": (">", 0),
                "promotion2_amount_used": (">", 0),
            },
            fields=["sum(promotion1_amount_used) as amount_used1", "sum(promotion2_amount_used) as amount_used2"],
        )[0]
        balance = 0
        if res:
            amount_used1 = balance_promotion.amount_used1 or 0
            amount_used2 = balance_promotion.amount_used2 or 0
            ending_balance = res[0].get('ending_balance') or 0
            promotion_balance_1 = res[0].get('promotion_balance_1') or 0
            promotion_balance_2 = res[0].get('promotion_balance_2') or 0
            balance = (ending_balance + promotion_balance_1 + promotion_balance_2) - (amount_used1 + amount_used2)
        
        return balance

    @frappe.whitelist()
    def get_detail_balance_all(self):
        res = frappe.db.get_all(
            "Balance Transaction",
            fields=['ending_balance', 'promotion_balance_1',
                    'promotion_balance_2'],
            filters={"team": self.name, "docstatus": 1},
            order_by="creation desc",
            limit=1,
        )
        
        balance_promotion = frappe.get_all(
            "Balance Transaction",
            filters={"docstatus": 1, "team": self.name},
            or_filters={
                "promotion1_amount_used": (">", 0),
                "promotion2_amount_used": (">", 0),
            },
            fields=["sum(promotion1_amount_used) as amount_used1", "sum(promotion2_amount_used) as amount_used2"],
        )[0]
        
        rs = {'ending_balance': 0, 'promotion_balance_1': 0, "promotion_balance_2": 0}
        if len(res):
            rs['ending_balance'] = (res[0].get('ending_balance') or 0)
            rs['promotion_balance_1'] = (res[0].get('promotion_balance_1') or 0) - (balance_promotion.amount_used1 or 0)
            rs['promotion_balance_2'] = (res[0].get('promotion_balance_2') or 0) - (balance_promotion.amount_used2 or 0)
        return rs

    def amount_owed(self):
        # số tiền còn nợ từ đăng ký gói site theo tháng
        return (
            frappe.get_all(
                "Invoice",
                {"status": "Unpaid", "team": self.name,
                 "type": "Subscription"},
                ["sum(amount_due) as amount_due"],
                pluck="amount_due",
            )[0]
            or 0
        )

    def get_list_promotion1(self):
        today = frappe.utils.today()
        
        arr = frappe.get_all(
                "Balance Transaction",
                fields=["name", "unallocated_amount_1", "promotion1_amount_used","date_promotion_1", "(COALESCE(unallocated_amount_1, 0) - COALESCE(promotion1_amount_used, 0)) AS remaining_amount"],
                filters = [
                    ['team', '=', self.name],
                    ['docstatus', '=', 1],
                    ['date_promotion_1', '>', today],
                    ['unallocated_amount_1', '>', 0]
                ],
                order_by="date_promotion_1 asc"
            )

        for tran in arr:
            tran.date_expire = get_date_expire_promotion(tran.name, tran.date_promotion_1)
        
        return arr
    
    def AI_amount(self):
        today = frappe.utils.today()
        start_time = frappe.utils.get_first_day(today).strftime('%Y-%m-%d')
        end_time = frappe.utils.get_last_day(today) + timedelta(days=1)
        end_time = end_time.strftime('%Y-%m-%d')

        return (
            frappe.get_all(
                "Request Service AI",
                filters = [
                    ['team', '=', self.name],
                    ['start_time', '>=', start_time],
                    ['start_time', '<', end_time]
                ],
                fields = ["sum(amount) as amount"],
                pluck="amount",
            )[0]
            or 0
        )

    def get_total_unpaid_amount(self):
        return self.amount_owed()

    @frappe.whitelist()
    def get_available_partner_credits(self):
        client = get_frappe_io_connection()
        response = client.session.post(
            f"{client.url}/api/method/partner_relationship_management.api.get_partner_credit_balance",
            data={"email": self.partner_email},
            headers=client.headers,
        )

        if response.ok:
            res = response.json()
            message = res.get("message")

            if message.get("credit_balance") is not None:
                return message.get("credit_balance")
            else:
                error_message = message.get("error_message")
                log_error(
                    "Partner Credit Fetch Error",
                    team=self.name,
                    email=self.partner_email,
                    error_message=error_message,
                )
                frappe.throw(error_message)

        else:
            log_error(
                "Problem fetching partner credit balance from frappe.io",
                team=self.name,
                email=self.partner_email,
                response=response.text,
            )
            frappe.throw("Problem fetching partner credit balance.")

    def is_partner_and_has_enough_credits(self):
        return self.erpnext_partner and self.get_balance_all() > 0

    def has_partner_account_on_erpnext_com(self):
        if frappe.conf.developer_mode:
            return False
        try:
            erpnext_com = get_erpnext_com_connection()
        except Exception:
            self.log_error(
                "Cannot connect to erpnext.com to check partner account")
            return False
        res = erpnext_com.get_value(
            "ERPNext Partner", "name", filters={"email": self.user, "status": "Approved"}
        )
        return res["name"] if res else None

    def can_create_site(self):
        why = ""
        allow = (True, "")

        if self.free_account or self.parent_team or self.is_saas_user or self.billing_team:
            return allow

        if self.payment_mode == "Partner Credits":
            if self.get_available_partner_credits() > 0:
                return allow
            else:
                why = "Không thể tạo tổ chức do không đủ điểm tín dụng đối tác"

        if self.payment_mode == "Prepaid Credits":
            if self.get_balance_all() > 0:
                return allow
            else:
                why = "Không thể tạo tổ chức do số dư không đủ"

        if self.payment_mode == "Card":
            if self.default_payment_method:
                return allow
            else:
                why = "Không thể tạo tổ chức mà không thêm thẻ"

        return (False, why)

    def can_install_paid_apps(self):
        if self.free_account or self.payment_mode == "Partner Credits" or self.billing_team:
            return True

        # bỏ điều kiện phải nạp tiền mới cho đổi plan
        return True

        return bool(
            frappe.db.exists(
                "Invoice", {"team": self.name,
                            "amount_paid": (">", 0), "status": "Paid"}
            )
        )

    def billing_info(self):
        return {
            "gst_percentage": frappe.db.get_single_value("Press Settings", "gst_percentage"),
            "balance": self.get_balance_all(),
            "verified_micro_charge": bool(
                frappe.db.exists(
                    "Stripe Payment Method", {
                        "team": self.name, "is_verified_with_micro_charge": 1}
                )
            ),
            "has_paid_before": bool(
                frappe.db.exists(
                    "Invoice", {"team": self.name,
                                "amount_paid": (">", 0), "status": "Paid"}
                )
            ),
        }

    def get_onboarding(self):
        if self.payment_mode == "Partner Credits":
            billing_setup = True
        else:
            billing_setup = bool(
                self.payment_mode in ["Card", "Prepaid Credits"]
                and (self.default_payment_method or self.get_balance_all() > 0)
                and self.billing_address
            )

        site_created = frappe.db.count("Site", {"team": self.name}) > 0

        if self.via_erpnext:
            erpnext_domain = frappe.db.get_single_value(
                "Press Settings", "erpnext_domain")
            erpnext_site = frappe.db.get_value(
                "Site",
                {"domain": erpnext_domain, "team": self.name,
                 "status": ("!=", "Archived")},
                ["name", "plan"],
                as_dict=1,
            )

            if erpnext_site is None:
                # Case: They have archived their ERPNext trial site
                # and created a frappe.cloud site now
                erpnext_site_plan_set = True
            else:
                erpnext_site_plan_set = erpnext_site.plan != "ERPNext Trial"
        else:
            erpnext_site = None
            erpnext_site_plan_set = True

        return frappe._dict(
            {
                "account_created": True,
                "billing_setup": billing_setup,
                "erpnext_site": erpnext_site,
                "erpnext_site_plan_set": erpnext_site_plan_set,
                "site_created": site_created,
                "complete": billing_setup and site_created and erpnext_site_plan_set,
            }
        )

    def get_route_on_login(self):
        if self.is_saas_user and not frappe.db.get_all("Site", {"team": self.name}, limit=1):
            saas_product = frappe.db.get_value(
                "SaaS Product Site Request",
                {"team": self.name, "status": "Pending"},
                "saas_product",
            )
            return f"/setup-site/{saas_product}"

        return "/sites"

    def get_pending_saas_site_request(self):
        if self.is_saas_user and not frappe.db.get_all("Site", {"team": self.name}, limit=1):
            return frappe.db.get_value(
                "SaaS Product Site Request",
                {"team": self.name, "status": "Pending"},
                "saas_product",
            )

    @frappe.whitelist()
    def suspend_sites(self, reason=None):
        sites_to_suspend = self.get_sites_to_suspend()
        for site in sites_to_suspend:
            try:
                frappe.get_doc("Site", site).suspend(reason)
            except Exception:
                log_error("Failed to Suspend Sites",
                          traceback=frappe.get_traceback())
        return sites_to_suspend

    def get_sites_to_suspend(self):
        plan = frappe.qb.DocType("Plan")
        query = (
            frappe.qb.from_(plan)
            .select(plan.name)
            .where(
                (plan.enabled == 1)
                & ((plan.is_frappe_plan == 1) | (plan.dedicated_server_plan == 1))
            )
        ).run(as_dict=True)
        dedicated_or_frappe_plans = [d.name for d in query]

        return frappe.db.get_all(
            "Site",
            {
                "team": self.name,
                "status": ("in", ("Active", "Inactive")),
                "free": 0,
                "plan": ("not in", dedicated_or_frappe_plans),
            },
            pluck="name",
        )

    @frappe.whitelist()
    def unsuspend_sites(self, reason=None):
        suspended_sites = [
            d.name for d in frappe.db.get_all("Site", {"team": self.name, "status": "Suspended"})
        ]
        for site in suspended_sites:
            frappe.get_doc("Site", site).unsuspend(reason)
        
        # gui email mo sites
        self.sendemail_open_sites()
        
        return suspended_sites
    
    def get_email_invoice(self):
        email = (
            frappe.db.get_value(
                "Communication Email", {
                    "parent": self.name, "type": "invoices"}, "value"
            )
            or self.user
        )
        return email
    
    
    def sendemail_open_sites(self):
        user = frappe.db.get_value('User', self.user, ['first_name', 'language'], as_dict=1)
        lang = user.language if user.language in ['vi', 'en'] else 'vi'
        
        email = self.get_email_invoice()
        date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        pre_subject = "[MBWCloud] - "
        subject = pre_subject + _('Your sites have been reactivated - {0}', lang).format(date_time)
        
        # get language template
        template = "site_open_email"
        template = f"{lang}_{template}"
        
        frappe.sendmail(
            recipients=email,
            subject=subject,
            template=template,
            args={
                "user_name": user.first_name if user else self.user,
            },
        )
    
    def available_balance(self):
        # hóa đơn chưa thanh toán của tháng
        invoice = self.get_upcoming_invoice()
        # tat cả số tiền còn nợ
        total_unpaid_amount = self.get_total_unpaid_amount()
        # tat ca so tien hien co
        amount_all = self.get_balance_all()
        
        amount_upcoming_invoice = invoice.total if invoice else 0
        # so tien còn nợ
        so_tien_con_no = amount_upcoming_invoice + total_unpaid_amount
        # so tien con lai sau khi trừ nợ
        balance = amount_all - so_tien_con_no
        
        return balance
    
    def get_upcoming_invoice(self):
        # get the current period's invoice
        today = frappe.utils.today()
        result = frappe.db.get_all(
            "Invoice",
            filters={
                "status": "Draft",
                "team": self.name,
                "type": "Subscription",
                "period_start": ("<=", today),
                "period_end": (">=", today),
            },
            order_by="creation desc",
            limit=1,
            pluck="name",
        )
        if result:
            return frappe.get_doc("Invoice", result[0])
        return None

    def create_upcoming_invoice(self):
        today = frappe.utils.today()
        return frappe.get_doc(
            doctype="Invoice", team=self.name, period_start=today, type="Subscription"
        ).insert()

    def notify_with_email(self, recipients: List[str], **kwargs):
        if not self.send_notifications:
            return
        if not recipients:
            recipients = [self.notify_email]

        frappe.sendmail(recipients=recipients, **kwargs)

    @frappe.whitelist()
    def send_telegram_alert_for_failed_payment(self, invoice):
        telegram = Telegram()
        team_url = get_url_to_form("Team", self.name)
        invoice_url = get_url_to_form("Invoice", invoice)
        telegram.send(
            f"Failed Invoice Payment [{invoice}]({invoice_url}) of"
            f" Partner: [{self.name}]({team_url})"
        )

    @frappe.whitelist()
    def send_email_for_failed_payment(self, invoice, sites=None):
        invoice = frappe.get_doc("Invoice", invoice)
        email = self.get_email_invoice()
        payment_method = self.default_payment_method
        # last_4 = frappe.db.get_value(
        #     "Stripe Payment Method", payment_method, "last_4")
        account_update_link = frappe.utils.get_url("/dashboard")

        lang = frappe.db.get_value('User', self.user, 'language')
        lang = lang if lang in ['vi', 'en'] else 'vi'
        
        pre_subject = "[MBWCloud] - "
        subject = pre_subject + _('Unsuccessful Invoice Payment During MBWCloud Registration', lang)

        # get language template
        template = "payment_failed_partner" if self.erpnext_partner else "payment_failed"
        template = f"{lang}_{template}"
        
        frappe.sendmail(
            recipients=email,
            subject=subject,
            template=template,
            args={
                "subject": subject,
                "payment_link": invoice.stripe_invoice_url,
                "amount": invoice.get_formatted("amount_due"),
                "account_update_link": account_update_link,
                # "last_4": last_4 or "",
                "card_not_added": not payment_method,
                "sites": sites,
                "team": self,
            },
        )


def get_team_members(team):
    if not frappe.db.exists("Team", team):
        return []

    r = frappe.db.get_all("Team Member", filters={
                          "parent": team}, fields=["user"])
    member_emails = [d.user for d in r]

    users = []
    if member_emails:
        users = frappe.db.sql(
            """
                select u.name, u.first_name, u.last_name, u.phone, GROUP_CONCAT(r.`role`) as roles
                from `tabUser` u
                left join `tabHas Role` r
                on (r.parent = u.name)
                where ifnull(u.name, '') in %s
                group by u.name
            """,
            [member_emails],
            as_dict=True,
        )
        for user in users:
            user.roles = (user.roles or "").split(",")

    return users


def get_child_team_members(team):
    if not frappe.db.exists("Team", team):
        return []

    # a child team cannot be parent to another child team
    if frappe.get_value("Team", team, "parent_team"):
        return []

    child_team_members = [
        d.name for d in frappe.db.get_all("Team", {"parent_team": team}, ["name"])
    ]

    child_teams = []
    if child_team_members:
        child_teams = frappe.db.sql(
            """
                select t.name, t.team_title, t.parent_team, t.user
                from `tabTeam` t
                where ifnull(t.name, '') in %s
                and t.enabled = 1
            """,
            [child_team_members],
            as_dict=True,
        )

    return child_teams


def get_default_team(user):
    if frappe.db.exists("Team", user):
        return user


def reset_used_and_noti_subscription(team):
    if team:
        frappe.db.sql(
            """
            UPDATE `tabSubscription`
            SET number_days_used = 0, estimated_number_of_notifications = 0
            WHERE team = %s
            """,
            (team,)
        )

def process_payos_webhook(doc, method):
    if doc.code != "00":
        return

    # Give them free credits too (only first time)
    team: Team = frappe.get_doc("Team", doc.team)
    team.allocate_free_credits()

    enqueue_finalize_unpaid_for_team(team.name)

def process_stripe_webhook(doc, method):
    """This method runs after a Stripe Webhook Log is created"""
    if doc.event_type not in ["payment_intent.succeeded"]:
        return

    event = frappe.parse_json(doc.payload)
    payment_intent = event["data"]["object"]
    if payment_intent.get("invoice"):
        # ignore payment for invoice
        return

    metadata = payment_intent.get("metadata")
    payment_for = metadata.get("payment_for")

    if payment_for and payment_for == "micro_debit_test_charge":
        process_micro_debit_test_charge(event)
        return

    if frappe.db.exists(
            "Invoice", {
                "stripe_payment_intent_id": payment_intent["id"], "status": "Paid"}
    ):
        # ignore creating if already allocated
        return

    team: Team = frappe.get_doc(
        "Team", {"stripe_customer_id": payment_intent["customer"]})
    amount = payment_intent["amount"] / 100
    gst = float(metadata.get("gst", 0))
    balance_transaction = team.allocate_credit_amount(
        amount - gst if gst else amount, source="Prepaid Credits", remark=payment_intent["id"]
    )

    # Give them free credits too (only first time)
    team.allocate_free_credits()

    # Telemetry: Added prepaid credits
    capture("added_card_or_prepaid_credits", "fc_signup", team.account_request)
    invoice = frappe.get_doc(
        doctype="Invoice",
        team=team.name,
        type="Prepaid Credits",
        status="Paid",
        due_date=datetime.fromtimestamp(payment_intent["created"]),
        amount_paid=amount,
        gst=gst or 0,
        total_before_tax=amount - gst,
        amount_due=amount,
        stripe_payment_intent_id=payment_intent["id"],
    )
    invoice.append(
        "items",
        {
            "description": "Prepaid Credits",
            "document_type": "Balance Transaction",
            "document_name": balance_transaction.name,
            "quantity": 1,
            "rate": amount,
        },
    )
    invoice.insert()
    invoice.reload()
    # there should only be one charge object
    charge = payment_intent["charges"]["data"][0]["id"]
    # update transaction amount, fee and exchange rate
    invoice.update_transaction_details(charge)
    invoice.submit()

    enqueue_finalize_unpaid_for_team(team.name)


def enqueue_finalize_unpaid_for_team(team: str):
    # get a list of unpaid invoices for the team
    invoices = frappe.get_all(
        "Invoice",
        filters={"team": team, "status": "Unpaid", "type": "Subscription"},
        pluck="name",
    )

    # Enqueue a background job to call finalize_draft_invoice
    for invoice in invoices:
        frappe.enqueue(
            "press.press.doctype.invoice.invoice.finalize_draft_invoice",
            invoice=invoice,
        )

    # neu khong thanh toan hoa don nao thi chay function unsuspend_sites_when_recharge
    if not invoices:
        unsuspend_sites_when_recharge(team)


def unsuspend_sites_when_recharge(team_name):
    team = frappe.get_doc("Team", team_name)
    if team.available_balance() > 0:
        reset_used_and_noti_subscription(team_name)
        team.unsuspend_sites('Nap tien vao TK MBWCloud')


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    user_type = frappe.db.get_value("User", user, "user_type", cache=True)
    if user_type == "System User":
        return ""

    team = get_current_team()

    return f"(`tabTeam`.`name` = {frappe.db.escape(team)})"


def has_permission(doc, ptype, user):
    if not user:
        user = frappe.session.user

    user_type = frappe.db.get_value("User", user, "user_type", cache=True)
    if user_type == "System User":
        return True

    team = get_current_team(True)
    child_team_members = [
        d.name for d in frappe.db.get_all("Team", {"parent_team": team.name}, ["name"])
    ]
    if doc.name == team.name or doc.name in child_team_members:
        return True

    return False


def validate_site_creation(doc, method):
    if frappe.session.user == "Administrator":
        return
    if not doc.team:
        return

    # validate site creation for team
    team = frappe.get_doc("Team", doc.team)
    [allow_creation, why] = team.can_create_site()
    print(allow_creation, why)
    if not allow_creation:
        frappe.throw(why)


def has_unsettled_invoices(team):
    return frappe.db.exists(
        "Invoice",
        {"team": team, "status": (
            "in", ("Unpaid", "Draft")), "type": "Subscription"},
    )


def is_us_eu():
    """Is the customer from U.S. or European Union"""
    countrygroup = [
        "United States",
        "United Kingdom",
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Republic of Cyprus",
        "Czech Republic",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Ireland",
        "Italy",
        "Latvia",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Poland",
        "Portugal",
        "Romania",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Switzerland",
        "Australia",
        "New Zealand",
        "Canada",
        "Mexico",
    ]
    return frappe.db.get_value("Team", get_current_team(), "country") in countrygroup
