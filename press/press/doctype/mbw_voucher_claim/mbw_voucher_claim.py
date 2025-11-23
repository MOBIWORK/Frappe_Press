# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWVoucherClaim(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount_used: DF.Float
		deducted_amount: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		status: DF.Literal["Active", "Unactive", "Disable"]
		type_voucher: DF.Literal["Marketing Signup", "Referral  Signup"]
		usage_status: DF.Literal["Used", "Unused"]
		voucher_id: DF.Link | None
	# end: auto-generated types
	
	def before_save(self):
		"""Auto-populate fields from the linked voucher"""
		if self.voucher_id:
			self.populate_voucher_details()
	
	def populate_voucher_details(self):
		if not self.voucher_id:
			return
		
		voucher = frappe.get_doc("MBW Voucher", self.voucher_id)
	
		self.deducted_amount = voucher.deducted_amount
		self.type_voucher = voucher.type_voucher

		if voucher.status == "Active":
			if not self.status:
				self.status = "Active"
		elif voucher.status == "Disable":
			if not self.status:
				self.status = "Disable"
		else:
			self.status = "Unactive"
