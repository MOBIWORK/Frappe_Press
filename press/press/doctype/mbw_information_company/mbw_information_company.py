# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWInformationCompany(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adress_name: DF.Data | None
		email_name: DF.Data | None
		full_name: DF.Data | None
		phone_number: DF.Data | None
		position_name: DF.Data | None
		representative_name: DF.Data | None
		tax_code: DF.Data | None
		team: DF.Link | None
	# end: auto-generated types
	pass
