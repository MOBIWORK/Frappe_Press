# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWLeadSource(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		code_source: DF.Data
		creator: DF.Link | None
		description: DF.TextEditor | None
		name_source: DF.Data
		status: DF.Literal["Active", "Unactive"]
	# end: auto-generated types
	
	def before_save(self):
		if not self.creator:
			self.creator = frappe.session.user
