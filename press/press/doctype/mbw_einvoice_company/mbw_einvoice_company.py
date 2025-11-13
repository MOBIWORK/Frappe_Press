# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWEInvoiceCompany(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_send_email: DF.Check
		api_url_development: DF.Data | None
		api_url_production: DF.Data | None
		bkav_email: DF.Data | None
		bkav_password: DF.Data | None
		company: DF.Data
		einvoice_provider: DF.Literal["BKAV eHoadon"]
		environment_type: DF.Literal["Production", "Testing"]
		invoice_form_bkav: DF.Data
		invoice_serial_bkav: DF.Data
		invoice_type: DF.Literal["Value-added tax invoice"]
		is_active: DF.Check
		language: DF.Literal["Vietnamese", "English"]
		partner_guid_bkav: DF.Data | None
		partner_token_bkav: DF.Data | None
		recipient_email: DF.Data | None
		tax_code: DF.Data | None
		webhook_url: DF.Data | None
	# end: auto-generated types
	pass
