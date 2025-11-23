# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWVoucher(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from press.press.doctype.mbw_voucher_app.mbw_voucher_app import MBWVoucherApp
		from press.press.doctype.mbw_voucher_campaign_source.mbw_voucher_campaign_source import MBWVoucherCampaignSource
		from press.press.doctype.mbw_voucher_lead_source.mbw_voucher_lead_source import MBWVoucherLeadSource

		app: DF.Table[MBWVoucherApp]
		code_voucher: DF.Data
		creator: DF.Link | None
		day_end: DF.Date | None
		day_start: DF.Date
		deducted_amount: DF.Float
		description: DF.TextEditor | None
		expiry_voucher: DF.Float
		image: DF.AttachImage | None
		issued_number_voucher: DF.Int
		max_number_voucher: DF.Int
		name_voucher: DF.Data
		referral_amount: DF.Float
		status: DF.Literal["Active", "Unactive", "Disable"]
		type_voucher: DF.Literal["Marketing Signup", "Referral  Signup"]
		voucher_campaign_source: DF.Table[MBWVoucherCampaignSource]
		voucher_lead_source: DF.Table[MBWVoucherLeadSource]
	# end: auto-generated types
	def before_save(self):
		if not self.creator :
			self.creator = frappe.session.user
