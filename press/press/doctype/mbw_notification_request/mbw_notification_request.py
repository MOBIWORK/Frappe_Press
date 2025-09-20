# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWNotificationRequest(Document):

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
		
		# Validate enum values
		valid_statuses = ["Ongoing", "Done"]
		valid_types = ["Restore", "Drop site", "Deactivate site"]
		
		if self.status and self.status not in valid_statuses:
			frappe.throw(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
		
		if self.type and self.type not in valid_types:
			frappe.throw(f"Invalid type. Must be one of: {', '.join(valid_types)}")
	
	def before_insert(self):
		"""Before insert hook"""
		# Set default status if not provided
		if not self.status:
			self.status = "Ongoing"
		
		# Set default description if not provided
		if not self.description:
			self.description = f"Request for {self.type.lower()} on site {self.site}"