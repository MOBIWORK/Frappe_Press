# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PayOsWebhookLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		code: DF.Data | None
		invoice_id: DF.Data | None
		message: DF.Text | None
		team: DF.Link
		webhook_body: DF.Code | None
	# end: auto-generated types
	pass
