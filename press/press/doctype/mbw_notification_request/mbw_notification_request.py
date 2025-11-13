# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWNotificationRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.TextEditor | None
		feedback: DF.TextEditor | None
		name_sender: DF.Data | None
		sender: DF.Link | None
		site: DF.Link | None
		status: DF.Literal["", "Ongoing", "Done"]
		type: DF.Literal["", "Restore", "Drop site", "Deactivate site", "payment", "voucher"]
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.TextEditor | None
		site: DF.Link | None
		status: DF.Literal["", "Ongoing", "Done"]
		type: DF.Literal["", "Restore", "Drop site", "Deactivate site"]

	dashboard_fields = [
		"site",
		"status", 
		"type",
		"description",
		"creation",
		"modified"
	]
	
	def validate(self):
		"""Validate MBW Notification Request"""
		# Validate site exists
		if self.site and not frappe.db.exists("Site", self.site):
			frappe.throw(f"Site '{self.site}' does not exist")
	
	def before_insert(self):
		"""Before insert hook"""
		# Set default status if not provided
		if not self.status:
			self.status = "Ongoing"
		
		# Set default description if not provided
		if not self.description:
			self.description = f"Request for {self.type.lower()} on site {self.site}"
			
	def after_insert(self):
		if not self.name_sender:
			self.name_sender = frappe.db.get_value("User", self.sender, "full_name")