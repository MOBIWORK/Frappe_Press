# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWEInvoiceSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		api_url_bkav: DF.Data | None
		api_url_bkav_dev: DF.Data | None
		enable_einvoice: DF.Check
		er_email_template_en: DF.Link | None
		er_email_template_vi: DF.Link | None
		link_web_bkav: DF.Data | None
		link_web_dev: DF.Data | None
		number_of_retries: DF.Int
	# end: auto-generated types
	pass
