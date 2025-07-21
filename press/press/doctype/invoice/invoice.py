# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate
from frappe.utils.data import fmt_money

from press.api.billing import get_stripe
from press.api.client import dashboard_whitelist
from press.utils import log_error
from press.utils.billing import (
	convert_stripe_money,
	get_frappe_io_connection,
	get_gateway_details,
	get_partner_external_connection,
	is_frappe_auth_disabled,
)


class Invoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from press.press.doctype.invoice_credit_allocation.invoice_credit_allocation import InvoiceCreditAllocation
		from press.press.doctype.invoice_discount.invoice_discount import InvoiceDiscount
		from press.press.doctype.invoice_item.invoice_item import InvoiceItem
		from press.press.doctype.invoice_transaction_fee.invoice_transaction_fee import InvoiceTransactionFee

		amended_from: DF.Link | None
		amount_due: DF.Currency
		amount_due_with_tax: DF.Currency
		amount_paid: DF.Currency
		applied_credits: DF.Currency
		billing_email: DF.Data | None
		credit_allocations: DF.Table[InvoiceCreditAllocation]
		currency: DF.Link | None
		customer_email: DF.Data | None
		customer_name: DF.Data | None
		customer_partnership_date: DF.Date | None
		discount_note: DF.Data | None
		discounts: DF.Table[InvoiceDiscount]
		due_date: DF.Date | None
		exchange_rate: DF.Float
		frappe_invoice: DF.Data | None
		frappe_partner_order: DF.Data | None
		frappe_partnership_date: DF.Date | None
		free_credits: DF.Currency
		gst: DF.Currency
		invoice_pdf: DF.Attach | None
		items: DF.Table[InvoiceItem]
		marketplace: DF.Check
		mpesa_invoice: DF.Data | None
		mpesa_invoice_pdf: DF.Attach | None
		mpesa_merchant_id: DF.Data | None
		mpesa_payment_record: DF.Data | None
		mpesa_receipt_number: DF.Data | None
		mpesa_request_id: DF.Data | None
		next_payment_attempt_date: DF.Date | None
		partner_email: DF.Data | None
		payment_attempt_count: DF.Int
		payment_attempt_date: DF.Date | None
		payment_date: DF.Date | None
		payment_mode: DF.Literal["", "Card", "Prepaid Credits", "NEFT", "Partner Credits", "Paid By Partner", "PayOS"]
		payos_checkout_url: DF.Text | None
		payos_order_code: DF.Data | None
		payos_payment_link_id: DF.Data | None
		payos_qr_code: DF.Text | None
		payos_status: DF.Data | None
		payos_transaction_datetime: DF.Datetime | None
		payos_transaction_ref: DF.Data | None
		period_end: DF.Date | None
		period_start: DF.Date | None
		razorpay_order_id: DF.Data | None
		razorpay_payment_id: DF.Data | None
		razorpay_payment_method: DF.Data | None
		razorpay_payment_record: DF.Link | None
		refund_reason: DF.Data | None
		status: DF.Literal["Draft", "Invoice Created", "Unpaid", "Paid", "Refunded", "Uncollectible", "Collected", "Empty"]
		stripe_invoice_id: DF.Data | None
		stripe_invoice_url: DF.Text | None
		stripe_payment_intent_id: DF.Data | None
		team: DF.Link
		total: DF.Currency
		total_before_discount: DF.Currency
		total_before_tax: DF.Currency
		total_discount_amount: DF.Currency
		transaction_amount: DF.Currency
		transaction_fee: DF.Currency
		transaction_fee_details: DF.Table[InvoiceTransactionFee]
		transaction_net: DF.Currency
		type: DF.Literal["Subscription", "Prepaid Credits", "Service", "Summary", "Partnership Fees"]
		vat_percentage: DF.Float
		write_off_amount: DF.Float
	# end: auto-generated types

	dashboard_fields = (
		"period_start",
		"period_end",
		"team",
		"items",
		"currency",
		"type",
		"payment_mode",
		"total",
		"total_before_discount",
		"total_before_tax",
		"partner_email",
		"amount_due",
		"amount_paid",
		"docstatus",
		"gst",
		"applied_credits",
		"status",
		"due_date",
		"total_discount_amount",
		"invoice_pdf",
		"stripe_invoice_url",
		"amount_due_with_tax",
		"mpesa_invoice",
		"mpesa_invoice_pdf",
	)

	@staticmethod
	def get_list_query(query, filters=None, **list_args):
		StripeWebhookLog = frappe.qb.DocType("Stripe Webhook Log")
		Invoice = frappe.qb.DocType("Invoice")

		partner_customer = filters.get("partner_customer")
		if partner_customer:
			team_name = filters.get("team")
			due_date = filters.get("due_date")
			filters.pop("partner_customer")
			query = (
				frappe.qb.from_(Invoice)
				.select(Invoice.name, Invoice.total, Invoice.amount_due, Invoice.status, Invoice.due_date)
				.where(
					(Invoice.team == team_name)
					& (Invoice.due_date >= due_date[1])
					& (Invoice.type == "Subscription")
				)
			)

		invoices = (
			query.select(StripeWebhookLog.name.as_("stripe_payment_failed"))
			.left_join(StripeWebhookLog)
			.on(
				(Invoice.name == StripeWebhookLog.invoice)
				& (StripeWebhookLog.event_type == "payment_intent.payment_failed")
			)
			.groupby(Invoice.name)
		).run(as_dict=True)

		for invoice in invoices:
			if stripe_log := invoice.stripe_payment_failed:
				payload, failed_payment_method = frappe.db.get_value(
					"Stripe Webhook Log", stripe_log, ["payload", "stripe_payment_method"]
				)
				payload = frappe.parse_json(payload)
				invoice.stripe_payment_error = (
					payload.get("data", {}).get("object", {}).get("last_payment_error", {}).get("message")
				)
				invoice.stripe_payment_failed_card = frappe.db.get_value(
					"Stripe Payment Method", failed_payment_method, "last_4"
				)

		return invoices

	def get_doc(self, doc):
		doc.invoice_pdf = self.invoice_pdf or (self.currency == "USD" and self.get_pdf())
		currency = frappe.get_value("Team", self.team, "currency")
		if currency == "USD":
			price_field = "price_usd"
			currency_symbol = "$"
		elif currency == "INR":
			price_field = "price_inr"
			currency_symbol = "₹"
		else:
			price_field = "price_vnd"  # VND làm mặc định
			currency_symbol = "₫"

		for item in doc["items"]:
			if item.document_type in ("Server", "Database Server"):
				item.document_name = frappe.get_value(item.document_type, item.document_name, "title")
				if server_plan := frappe.get_value("Server Plan", item.plan, price_field):
					item.plan = f"{currency_symbol}{server_plan}"
				elif server_plan := frappe.get_value("Server Storage Plan", item.plan, price_field):
					item.plan = f"Storage Add-on {currency_symbol}{server_plan}/GB"
			elif item.document_type == "Marketplace App":
				item.document_name = frappe.get_value(item.document_type, item.document_name, "title")
				item.plan = (
					f"{currency_symbol}{frappe.get_value('Marketplace App Plan', item.plan, price_field)}"
				)

	@dashboard_whitelist()
	def stripe_payment_url(self):
		if not self.stripe_invoice_id:
			return
		frappe.response.location = self.get_stripe_payment_url()
		frappe.response.type = "redirect"

	def get_stripe_payment_url(self):
		stripe_link_expired = (
			self.status == "Unpaid" and frappe.utils.date_diff(frappe.utils.now(), self.due_date) > 30
		)
		if stripe_link_expired:
			stripe = get_stripe()
			stripe_invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
			url = stripe_invoice.hosted_invoice_url
		else:
			url = self.stripe_invoice_url
		return url

	def validate(self):
		self.set_default_vat_percentage()
		self.validate_team()
		self.validate_dates()
		self.validate_duplicate()
		self.validate_items()
		self.calculate_values()
		self.compute_free_credits()

	def set_default_vat_percentage(self):
		"""Set default VAT percentage from Press Settings if not already set"""
		if not self.vat_percentage:
			default_vat = frappe.db.get_single_value("Press Settings", "vat_percentage")
			if default_vat:
				self.vat_percentage = default_vat

	def before_submit(self):
		if self.total > 0 and self.status != "Paid":
			frappe.throw("Invoice must be Paid to be submitted")

	def calculate_values(self):
		if self.status == "Paid" and self.docstatus == 1:
			# don't calculate if already invoice is paid and already submitted
			return
		self.calculate_total()
		self.calculate_discounts()
		self.calculate_amount_due()
		self.apply_taxes_if_applicable()

	@frappe.whitelist()
	def finalize_invoice(self):  # noqa: C901
		if self.type == "Prepaid Credits":
			return

		# SET FLAG để chặn PayOS tạo trùng lặp trong quá trình finalize
		self._is_finalizing = True
		self._skip_payos_update = True

		try:
			self.calculate_values()

			if self.total == 0:
				self.status = "Empty"
				self.submit()
				return

			team = frappe.get_doc("Team", self.team)
			if not team.enabled:
				self.add_comment("Info", "Skipping finalize invoice because team is disabled")
				self.save()
				return

			if self.stripe_invoice_id:
				# if stripe invoice is already created and paid,
				# then update status and return early
				stripe = get_stripe()
				invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
				if invoice.status == "paid":
					self.status = "Paid"
					self.update_transaction_details(invoice.charge)
					self.submit()
					self.unsuspend_sites_if_applicable()
					return

			# set as unpaid by default
			self.status = "Unpaid"
			self.update_item_descriptions()

			if self.amount_due > 0:
				self.apply_credit_balance()

			if self.amount_due == 0:
				self.status = "Paid"

			if self.status == "Paid" and self.stripe_invoice_id and self.amount_paid == 0:
				stripe = get_stripe()
				invoice = stripe.Invoice.retrieve(self.stripe_invoice_id)
				payment_intent = stripe.PaymentIntent.retrieve(invoice.payment_intent)
				if payment_intent.status == "processing":
					# mark the fc invoice as Paid
					# if the payment intent is processing, it means the invoice cannot be voided yet
					# wait for invoice to be updated and then mark it as void if payment failed
					# or issue a refund if succeeded
					self.save()  # status is already Paid, so no need to set again
				else:
					self.change_stripe_invoice_status("Void")
					self.add_comment(
						text=(
							f"Stripe Invoice {self.stripe_invoice_id} voided because payment is done via credits."
						)
					)

			self.save()

			if self.amount_due > 0:
				if self.payment_mode == "Prepaid Credits":
					self.add_comment(
						"Comment",
						"Not enough credits for this invoice. Change payment mode to Card to pay using Stripe.",
					)
				# we shouldn't depend on payment_mode to decide whether to create stripe invoice or not
				# there should be a separate field in team to decide whether to create automatic invoices or not
				if self.payment_mode == "Card":
					self.create_stripe_invoice()

			if self.status == "Paid":
				self.submit()
				self.unsuspend_sites_if_applicable()

		finally:
			# Reset flags sau khi finalize xong
			self._is_finalizing = False
			self._skip_payos_update = False
			
			# ✅ THÊM: Tự động tạo PayOS link sau khi finalize nếu chưa có
			try:
				# Chỉ tạo PayOS link nếu:
				# 1. Invoice đã finalize thành công
				# 2. Chưa có PayOS order code
				# 3. Invoice có giá trị > 0
				# 4. Không phải Prepaid Credits type
				# 5. Status là Unpaid (cần thanh toán)
				if (self.status == "Unpaid" and 
					not self.get('payos_order_code') and 
					self.get('total', 0) > 0 and 
					self.get('type') != 'Prepaid Credits'):
					
					from press.api.app_admin import create_payment_link_internal
					print(f"🔄 Creating PayOS link after finalize for {self.name} - Amount: {self.total:,.0f} VND")
					
					result = create_payment_link_internal(self.name)
					if result.get('success') and result.get('data'):
						self.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
						self.db_set('payos_qr_code', result['data'].get('qr_code', ''))
						self.db_set('payos_order_code', result['data'].get('order_code', ''))
						self.db_set('payos_status', 'PENDING')
						print(f"✅ PayOS link created after finalize: {result['data'].get('order_code')}")
						
						# Log thành công
						frappe.log_error(
							f"PayOS payment link created after finalize for Invoice {self.name} - Order: {result['data'].get('order_code')}", 
							'PayOS Finalize Creation Success'
						)
					else:
						print(f"❌ Failed to create PayOS link after finalize: {result.get('message')}")
						frappe.log_error(f"Failed to create PayOS link after finalize for Invoice {self.name}: {result.get('message', 'Unknown error')}", 'PayOS Finalize Creation Error')
				else:
					print(f"⏭️ Skip PayOS creation after finalize for {self.name}: status={self.status}, order_code={bool(self.get('payos_order_code'))}, total={self.get('total', 0)}, type={self.get('type')}")
					
			except Exception as e:
				frappe.log_error(f"Error creating PayOS link after finalize for Invoice {self.name}: {str(e)}\n{frappe.get_traceback()}", 'PayOS Finalize Creation Exception')
				print(f"❌ Exception creating PayOS after finalize: {str(e)}")

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

	def calculate_total(self):
		total = 0
		for item in self.items:
			total += item.amount
		self.total = flt(total, 2)

	def apply_taxes_if_applicable(self):
		self.amount_due_with_tax = self.amount_due
		self.gst = 0

		if self.payment_mode == "Prepaid Credits":
			return

		# SỬA LOGIC VAT ĐỂ HỖ TRỢ VND VÀ SỬ DỤNG VAT_PERCENTAGE
		if self.currency == "INR" and self.type == "Subscription":
			gst_rate = frappe.db.get_single_value("Press Settings", "gst_percentage")
			self.gst = flt(self.amount_due * gst_rate, 2)
			self.amount_due_with_tax = flt(self.amount_due + self.gst, 2)
		elif self.currency == "VND" and self.type == "Subscription":
			# SỬ DỤNG VAT_PERCENTAGE CHO VND
			vat_rate = float(self.get('vat_percentage', 0) or 0) / 100  # Chuyển % thành decimal
			if vat_rate > 0:
				self.gst = flt(self.amount_due * vat_rate, 2)
				self.amount_due_with_tax = flt(self.amount_due + self.gst, 2)
				print(f"💰 VAT calculation for {self.name}: {self.amount_due:,.0f} + VAT {self.vat_percentage}% = {self.amount_due_with_tax:,.0f} VND")
			else:
				print(f"💰 No VAT for {self.name}: {self.amount_due:,.0f} VND")
		elif self.vat_percentage and self.vat_percentage > 0:
			# FALLBACK: Áp dụng VAT cho các currency khác nếu có vat_percentage
			vat_rate = float(self.vat_percentage) / 100
			self.gst = flt(self.amount_due * vat_rate, 2)
			self.amount_due_with_tax = flt(self.amount_due + self.gst, 2)
			print(f"💰 VAT calculation for {self.name} ({self.currency}): {self.amount_due:,.2f} + VAT {self.vat_percentage}% = {self.amount_due_with_tax:,.2f}")
		else:
			print(f"💰 No VAT applicable for {self.name} ({self.currency}): {self.amount_due:,.2f}")

	def calculate_amount_due(self):
		self.amount_due = flt(self.total - self.applied_credits, 2)
		if self.amount_due < 0 and self.amount_due > -0.1:
			self.write_off_amount = self.amount_due
			self.amount_due = 0

		if self.amount_due > 0 and self.amount_due < 0.1:
			self.write_off_amount = self.amount_due
			self.amount_due = 0

	def on_submit(self):
		self.create_invoice_on_frappeio()
		self.fetch_mpesa_invoice_pdf()

	def on_update_after_submit(self):
		self.create_invoice_on_frappeio()
		self.fetch_mpesa_invoice_pdf()

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

		# --- Tự động tạo PayOS payment link khi tạo mới invoice ---
		# CHẶN VIỆC TẠO TRÙNG LẶP
		try:
			# Chỉ tạo PayOS link nếu:
			# 1. Chưa có PayOS order code
			# 2. Invoice có giá trị > 0
			# 3. Không phải Prepaid Credits type
			# 4. Không phải trong quá trình finalize
			if (not self.get('payos_order_code') and 
				self.get('total', 0) > 0 and 
				self.get('type') != 'Prepaid Credits' and
				not getattr(self, '_skip_payos_creation', False)):
				
				from press.api.app_admin import create_payment_link_internal
				print(f"🎯 Creating initial PayOS link for {self.name} - Amount: {self.total:,.0f} VND")
				result = create_payment_link_internal(self.name)
				if result.get('success') and result.get('data'):
					self.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
					self.db_set('payos_qr_code', result['data'].get('qr_code', ''))
					self.db_set('payos_order_code', result['data'].get('order_code', ''))
					self.db_set('payos_status', 'PENDING')
					print(f"✅ PayOS link created: {result['data'].get('order_code')}")
				else:
					frappe.log_error(result.get('message', 'Unknown error'), 'PayOS Auto Payment Link Error')
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), 'PayOS Auto Payment Link Exception')

	def create_stripe_invoice(self):
		if self.stripe_invoice_id:
			invoice = self.get_stripe_invoice()
			stripe_invoice_total = convert_stripe_money(invoice.total)
			if self.amount_due_with_tax == stripe_invoice_total:
				# return if an invoice with the same amount is already created
				return
			# if the amount is changed, void the stripe invoice and create a new one
			self.change_stripe_invoice_status("Void")
			formatted_amount = fmt_money(stripe_invoice_total, currency=self.currency)
			self.add_comment(
				text=(f"Stripe Invoice {self.stripe_invoice_id} of amount {formatted_amount} voided.")
			)
			self.stripe_invoice_id = ""
			self.stripe_invoice_url = ""
			self.save()

		if self.amount_due_with_tax <= 0:
			return

		customer_id = frappe.db.get_value("Team", self.team, "stripe_customer_id")
		amount = int(self.amount_due_with_tax * 100)
		self._make_stripe_invoice(customer_id, amount)

	def mandate_inactive(self, mandate_id):
		stripe = get_stripe()
		mandate = stripe.Mandate.retrieve(mandate_id)
		return mandate.status in ("inactive", "pending")

	def _make_stripe_invoice(self, customer_id, amount):
		mandate_id = self.get_mandate_id(customer_id)
		if mandate_id and self.mandate_inactive(mandate_id):
			frappe.db.set_value("Invoice", self.name, "payment_mode", "Prepaid Credits")
			self.reload()
			return None
		try:
			stripe = get_stripe()
			invoice = stripe.Invoice.create(
				customer=customer_id,
				pending_invoice_items_behavior="exclude",
				collection_method="charge_automatically",
				auto_advance=True,
				currency=self.currency.lower(),
				payment_settings={"default_mandate": mandate_id},
				idempotency_key=f"invoice:{self.name}:amount:{amount}",
			)
			stripe.InvoiceItem.create(
				customer=customer_id,
				invoice=invoice["id"],
				description=self.get_stripe_invoice_item_description(),
				amount=amount,
				currency=self.currency.lower(),
				idempotency_key=f"invoiceitem:{self.name}:amount:{amount}",
			)
			self.db_set(
				{
					"stripe_invoice_id": invoice["id"],
					"status": "Invoice Created",
				},
				commit=True,
			)
			self.reload()
			return invoice
		except Exception:
			frappe.db.rollback()
			self.reload()

			# log the traceback as comment
			msg = "<pre><code>" + frappe.get_traceback() + "</pre></code>"
			self.add_comment("Comment", _("Stripe Invoice Creation Failed") + "<br><br>" + msg)
			frappe.db.commit()

	def get_mandate_id(self, customer_id):
		mandate_id = frappe.get_value(
			"Stripe Payment Method", {"team": self.team, "is_default": 1}, "stripe_mandate_id"
		)
		if not mandate_id:
			return ""
		return mandate_id

	def find_stripe_invoice_if_not_set(self):
		if self.stripe_invoice_id:
			return
		# if stripe invoice was created, find it and set it
		# so that we avoid scenarios where Stripe Invoice was created but not set in Frappe Cloud
		stripe = get_stripe()
		invoices = stripe.Invoice.list(customer=frappe.db.get_value("Team", self.team, "stripe_customer_id"))
		description = self.get_stripe_invoice_item_description()
		for invoice in invoices.data:
			line_items = invoice.lines.data
			if line_items and line_items[0].description == description and invoice.status != "void":
				self.stripe_invoice_id = invoice["id"]
				self.status = "Invoice Created"
				self.save()

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
		invoice_exists = frappe.db.exists(
			"Invoice",
			{
				"stripe_payment_intent_id": self.stripe_payment_intent_id,
				"type": "Prepaid Credits",
				"name": ("!=", self.name),
			},
		)
		if self.type == "Prepaid Credits" and self.stripe_payment_intent_id and invoice_exists:
			frappe.throw("Invoice with same Stripe payment intent exists", frappe.DuplicateEntryError)

		if self.type == "Subscription" and self.period_start and self.period_end and self.is_new():
			query = (
				f"select `name` from `tabInvoice` where team = '{self.team}' and"
				f" status = 'Draft' and ('{self.period_start}' between `period_start` and"
				f" `period_end` or '{self.period_end}' between `period_start` and"
				" `period_end`)"
			)

			intersecting_invoices = [x[0] for x in frappe.db.sql(query, as_list=True)]

			if intersecting_invoices:
				frappe.throw(
					f"There are invoices with intersecting periods:{', '.join(intersecting_invoices)}",
					frappe.DuplicateEntryError,
				)

	def validate_team(self):
		team = frappe.get_doc("Team", self.team)

		self.customer_name = team.billing_name or frappe.utils.get_fullname(self.team)
		self.customer_email = (
			frappe.db.get_value("Communication Email", {"parent": team.user, "type": "invoices"}, ["value"])
			or team.user
		)
		self.currency = team.currency
		if not self.payment_mode:
			self.payment_mode = team.payment_mode
		if not self.currency:
			frappe.throw(f"Cannot create Invoice because Currency is not set in Team {self.team}")

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
			if not item.description:
				how_many_days = f"{cint(item.quantity)} day{'s' if item.quantity > 1 else ''}"
				if item.document_type == "Site" and item.plan:
					site_name = item.document_name.split(".archived")[0]
					plan = frappe.get_cached_value("Site Plan", item.plan, "plan_title")
					item.description = f"{site_name} active for {how_many_days} on {plan} plan"
				elif item.document_type in ["Server", "Database Server"]:
					server_title = frappe.get_cached_value(item.document_type, item.document_name, "title")
					if item.plan == "Add-on Storage plan":
						item.description = f"{server_title} Storage Add-on for {how_many_days}"
					else:
						item.description = f"{server_title} active for {how_many_days}"
				elif item.document_type == "Marketplace App":
					app_title = frappe.get_cached_value("Marketplace App", item.document_name, "title")
					item.description = f"Marketplace app {app_title} active for {how_many_days}"
				else:
					item.description = "Prepaid Credits"

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

		self.save()
		usage_record.db_set("invoice", self.name)
		
		# ✅ THÊM: Tự động tạo PayOS payment link sau khi thêm usage record
		try:
			# Chỉ tạo PayOS link nếu:
			# 1. Chưa có PayOS order code
			# 2. Invoice có giá trị > 0 sau khi thêm usage record
			# 3. Không phải Prepaid Credits type
			# 4. Không đang trong quá trình finalize
			if (not self.get('payos_order_code') and 
				self.get('total', 0) > 0 and 
				self.get('type') == 'Subscription' and
				not getattr(self, '_skip_payos_creation', False) and
				not getattr(self, '_is_finalizing', False)):
				
				from press.api.app_admin import create_payment_link_internal
				
				result = create_payment_link_internal(self.name)
				if result.get('success') and result.get('data'):
					self.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
					self.db_set('payos_qr_code', result['data'].get('qr_code', ''))
					self.db_set('payos_order_code', result['data'].get('order_code', ''))
					self.db_set('payos_status', 'PENDING')
					
					# Log thành công
					frappe.log_error(
						f"PayOS payment link created after adding usage record for Invoice {self.name} - Order: {result['data'].get('order_code')}", 
						'PayOS Usage Record Creation Success'
					)
				else:

					frappe.log_error(f"Failed to create PayOS link after usage record for Invoice {self.name}: {result.get('message', 'Unknown error')}", 'PayOS Usage Record Creation Error')
			else:
				print(f"⏭️ Skip PayOS creation after usage record for {self.name}: "
					f"order_code={bool(self.get('payos_order_code'))}, "
					f"total={self.get('total', 0)}, "
					f"type={self.get('type')}, "
					f"skip_creation={getattr(self, '_skip_payos_creation', False)}")
				
		except Exception as e:
			frappe.log_error(f"Error creating PayOS link after usage record for Invoice {self.name}: {str(e)}\n{frappe.get_traceback()}", 'PayOS Usage Record Exception')

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
				row.amount = flt((row.quantity * row.rate), 2)

		for item in items_to_remove:
			self.remove(item)

	def compute_free_credits(self):
		self.free_credits = sum([d.amount for d in self.credit_allocations if d.source == "Free Credits"])

	def calculate_discounts(self):
		for item in self.items:
			if item.discount_percentage:
				item.discount = flt(item.amount * (item.discount_percentage / 100), 2)

		self.total_discount_amount = sum([item.discount for item in self.items]) + sum(
			[d.amount for d in self.discounts]
		)

		npo_discount_applicable = frappe.db.get_value("Team", self.team, "apply_npo_discount")
		if npo_discount_applicable:
			npo_discount = frappe.db.get_single_value("Press Settings", "npo_discount")
			if npo_discount:
				self.total_discount_amount += flt(self.total * (npo_discount / 100), 2)

		self.total_before_discount = self.total
		self.total = flt(self.total_before_discount - self.total_discount_amount, 2)

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
				description=f"Reversed on cancel of Invoice {self.name}",
			)
			doc.insert()
			doc.submit()

	def apply_credit_balance(self):
		# previously we used to cancel and re-apply credits, but it messed up the balance transaction history
		# so now we only do append-only operation while applying credits

		balance = frappe.get_cached_doc("Team", self.team).get_balance()
		if balance <= 0:
			return

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

		total_allocated = 0
		due = self.amount_due
		for balance in unallocated_balances:
			if due == 0:
				break
			allocated = min(due, balance.unallocated_amount)
			due -= allocated
			self.append(
				"credit_allocations",
				{
					"transaction": balance.name,
					"amount": allocated,
					"currency": self.currency,
					"source": balance.source,
				},
			)
			doc = frappe.get_doc("Balance Transaction", balance.name)
			doc.append(
				"allocated_to",
				{"invoice": self.name, "amount": allocated, "currency": self.currency},
			)
			doc.save()
			total_allocated += allocated

		balance_transaction = frappe.get_doc(
			doctype="Balance Transaction",
			team=self.team,
			type="Applied To Invoice",
			amount=total_allocated * -1,
			invoice=self.name,
		).insert()
		balance_transaction.submit()

		self.applied_credits = sum(row.amount for row in self.credit_allocations)
		self.calculate_values()

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

		if already_exists:
			return None

		# ✅ SỬA LỖI CHÍNH: Tạo invoice mới và đảm bảo PayOS link được tạo
		new_invoice = frappe.get_doc(doctype="Invoice", team=self.team, period_start=next_start)
		
		# Đảm bảo không có flag chặn PayOS creation
		new_invoice._skip_payos_creation = False
		new_invoice._skip_payos_update = False
		
		# Insert invoice mới
		new_invoice.insert()
		
		# ✅ THÊM: Tự động tạo PayOS payment link nếu chưa có
		try:
			# Kiểm tra sau khi insert xem đã có PayOS link chưa
			new_invoice.reload()
			if (not new_invoice.get('payos_order_code') and 
				new_invoice.get('total', 0) > 0 and 
				new_invoice.get('type') != 'Prepaid Credits'):
				
				from press.api.app_admin import create_payment_link_internal

				
				result = create_payment_link_internal(new_invoice.name)
				if result.get('success') and result.get('data'):
					new_invoice.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
					new_invoice.db_set('payos_qr_code', result['data'].get('qr_code', ''))
					new_invoice.db_set('payos_order_code', result['data'].get('order_code', ''))
					new_invoice.db_set('payos_status', 'PENDING')

					
					# Log thành công
					frappe.log_error(
						f"PayOS payment link created for next invoice {new_invoice.name} - Order: {result['data'].get('order_code')}", 
						'PayOS Auto Creation Success'
					)
				else:

					frappe.log_error(f"Failed to create PayOS link for next invoice {new_invoice.name}: {result.get('message', 'Unknown error')}", 'PayOS Next Invoice Error')
			else:
				print(f"⏭️ Skip PayOS creation for next invoice {new_invoice.name}: order_code={bool(new_invoice.get('payos_order_code'))}, total={new_invoice.get('total', 0)}, type={new_invoice.get('type')}")
				
		except Exception as e:
			frappe.log_error(f"Error creating PayOS link for next invoice {new_invoice.name}: {str(e)}\n{frappe.get_traceback()}", 'PayOS Next Invoice Exception')

		return new_invoice

	def on_update(self):
		"""
		Hook được gọi mỗi khi Invoice được cập nhật
		Kiểm tra và cập nhật PayOS payment link nếu số tiền thay đổi
		"""
		# CHỈ XỬ LÝ PAYOS NẾU KHÔNG TRONG QUÁ TRÌNH FINALIZE
		if not getattr(self, '_skip_payos_update', False):
			self.update_payos_payment_link_if_amount_changed()

	def update_payos_payment_link_if_amount_changed(self):
		"""
		Cập nhật PayOS payment link nếu số tiền invoice thay đổi
		"""
		try:
			# CHẶN XỬ LÝ TRONG CÁC TRƯỜNG HỢP SAU:
			# 1. Chưa có PayOS order code (chưa từng tạo payment link)
			# 2. Invoice đã thanh toán 
			# 3. PayOS status không phải PENDING
			# 4. Invoice type là Prepaid Credits
			# 5. Đang trong quá trình finalize/create
			if (not self.get('payos_order_code') or 
				self.get('status') == 'Paid' or 
				self.get('payos_status') not in ['PENDING', None, ''] or
				self.get('type') == 'Prepaid Credits' or
				getattr(self, '_skip_payos_update', False) or
				getattr(self, '_is_finalizing', False)):
				
				
				# ✅ THÊM LOGIC MỚI: Tạo PayOS link cho invoice chưa có link và có total > 0
				if (not self.get('payos_order_code') and 
					self.get('total', 0) > 0 and 
					self.get('type') != 'Prepaid Credits' and
					not getattr(self, '_skip_payos_update', False)):
					
					from press.api.app_admin import create_payment_link_internal

					
					result = create_payment_link_internal(self.name)
					if result.get('success') and result.get('data'):
						self.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
						self.db_set('payos_qr_code', result['data'].get('qr_code', ''))
						self.db_set('payos_order_code', result['data'].get('order_code', ''))
						self.db_set('payos_status', 'PENDING')

						
						# Log thành công
						frappe.log_error(
							f"PayOS payment link created for updated Invoice {self.name} - Order: {result['data'].get('order_code')}", 
							'PayOS Update Creation Success'
						)
					else:
						frappe.log_error(f"Failed to create PayOS link for updated Invoice {self.name}: {result.get('message', 'Unknown error')}", 'PayOS Update Creation Error')
				
				return
			
			# Kiểm tra xem số tiền có thay đổi không
			if hasattr(self, '_doc_before_save'):
				old_total = self._doc_before_save.get('total', 0) or 0
				new_total = self.get('total', 0) or 0
				
				# Nếu số tiền thay đổi đáng kể (> 1000 VND)
				if abs(new_total - old_total) > 1000:
					print(f"💰 Invoice {self.name} amount changed: {old_total:,.0f} → {new_total:,.0f} VND")
					
					# Hủy payment link cũ và tạo mới
					if self.get('payos_order_code'):
						self.cancel_old_payos_payment_link()
						self.create_new_payos_payment_link()

		except Exception as e:
			frappe.log_error(f"Error updating PayOS payment link for Invoice {self.name}: {str(e)}\n{frappe.get_traceback()}", 'PayOS Update Exception')


	def cancel_old_payos_payment_link(self):
		"""
		Hủy PayOS payment link cũ
		"""
		try:
			if not self.get('payos_order_code'):
				return
				
			from press.api.payos_connect import cancel_payos_payment
			result = cancel_payos_payment(self.get('payos_order_code'), "Amount changed")
			
			if result.get('success'):
				print(f"✅ Cancelled old PayOS link: {self.get('payos_order_code')}")
			else:
				print(f"⚠️ Failed to cancel old PayOS link: {result.get('message')}")
				
		except Exception as e:
			frappe.log_error(f"Error cancelling old PayOS link: {str(e)}", 'PayOS Cancel Error')

	def create_new_payos_payment_link(self):
		"""
		Tạo PayOS payment link mới với số tiền cập nhật
		"""
		try:
			# Reset PayOS fields
			self.db_set('payos_order_code', '')
			self.db_set('payos_checkout_url', '')
			self.db_set('payos_qr_code', '')
			self.db_set('payos_status', '')
			
			# Tạo payment link mới
			from press.api.app_admin import create_payment_link_internal
			print(f"🔄 Creating new PayOS link for {self.name} - Amount: {self.total:,.0f} VND")
			
			result = create_payment_link_internal(self.name)
			if result.get('success') and result.get('data'):
				self.db_set('payos_checkout_url', result['data'].get('checkout_url', ''))
				self.db_set('payos_qr_code', result['data'].get('qr_code', ''))
				self.db_set('payos_order_code', result['data'].get('order_code', ''))
				self.db_set('payos_status', 'PENDING')
				print(f"✅ New PayOS link created: {result['data'].get('order_code')}")
				
				# Log thành công
				frappe.log_error(
					f"New PayOS payment link created for Invoice {self.name} - Order: {result['data'].get('order_code')}", 
					'PayOS Recreate Success'
				)
			else:
				print(f"❌ Failed to create new PayOS link: {result.get('message')}")
				frappe.log_error(f"Failed to create new PayOS link for Invoice {self.name}: {result.get('message', 'Unknown error')}", 'PayOS Recreate Error')
				
		except Exception as e:
			frappe.log_error(f"Error creating new PayOS link: {str(e)}", 'PayOS Recreate Exception')

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
		log_error("Invoice creation for next month failed", invoice=invoice.name)


def calculate_gst(amount):
	return amount * 0.18


def get_permission_query_conditions(user):
	from press.utils import get_current_team
	if not user:
		user = frappe.session.user

	user_type = frappe.db.get_value("User", user, "user_type", cache=True)
	if user_type == "System User":
		return ""

	team = get_current_team()

	return f"(`tabInvoice`.`team` = {frappe.db.escape(team)})"


def has_permission(doc, ptype, user):
	from press.utils import get_current_team, has_role
	if not user:
		user = frappe.session.user

	user_type = frappe.db.get_value("User", user, "user_type", cache=True)
	if user_type == "System User":
		return True

	if ptype == "create":
		return True

	if has_role("Press Support Agent", user) and ptype == "read":
		return True

	team = get_current_team(True)
	team_members = [
		d.user for d in frappe.db.get_all("Team Member", {"parenttype": "Team", "parent": doc.team}, ["user"])
	]
	if doc.team == team.name or team.user in team_members:
		return True
	return False


# M-pesa external site for webhook
def create_sales_invoice_on_external_site(transaction_response):
	client = get_partner_external_connection()
	try:
		# Define the necessary data for the Sales Invoice creation
		data = {
			"customer": transaction_response.get("team"),
			"posting_date": frappe.utils.nowdate(),
			"due_date": frappe.utils.add_days(frappe.utils.nowdate(), 30),
			"items": [
				{
					"item_code": "Frappe Cloud Payment",
					"qty": 1,
					"rate": transaction_response.get("Amount"),
					"description": "Payment for Mpesa transaction",
				}
			],
			"paid_amount": transaction_response.get("Amount"),
			"status": "Paid",
		}

		# Post to the external site's sales invoice creation API
		response = client.session.post(
			f"{client.url}/api/method/frappe.client.insert",
			headers=client.headers,
			json={"doc": data},
		)

		if response.ok:
			res = response.json()
			sales_invoice = res.get("message")
			if sales_invoice:
				frappe.msgprint(_("Sales Invoice created successfully on external site."))
				return sales_invoice
		else:
			frappe.throw(_("Failed to create Sales Invoice on external site."))
	except Exception as e:
		frappe.log_error(str(e), "Error creating Sales Invoice on external site")
