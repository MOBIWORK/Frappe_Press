# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWDetailEInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action: DF.Literal["Create invoice", "Sign invoice", "Update status", "Revoke invoice", "Get token"]
		attached_data: DF.JSON | None
		bkav_invoice_id: DF.Data | None
		company: DF.Data
		end_time: DF.Datetime | None
		invoice_form: DF.Data | None
		invoice_name: DF.Data
		invoice_serial: DF.Data | None
		is_retry: DF.Check
		json_data: DF.JSON | None
		lookup_code: DF.Data | None
		message_log: DF.HTMLEditor | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		publisher: DF.Link | None
		release_date: DF.Datetime | None
		retry_num: DF.Int
		start_time: DF.Datetime | None
		status: DF.Literal["Pending processing", "Successful", "Failed", "Cancelled"]
		status_einvoice: DF.Literal["", "Newly created", "Pending issuance", "Pending revocation", "Pending adjustment", "Pending replacement", "Replacement", "Replaced", "Issued", "Revoked", "Adjustment", "Adjusted", "Not in use"]
		supplier: DF.Data | None
		tax_status_einvoice: DF.Literal["", "Pending approval", "Signed", "Rejected", "Sent", "Error", "Pending signature"]
		view_url: DF.Data | None
	# end: auto-generated types
	pass
