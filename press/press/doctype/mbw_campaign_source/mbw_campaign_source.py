# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWCampaignSource(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from press.press.doctype.mbw_campaign_app.mbw_campaign_app import MBWCampaignApp

		app: DF.Table[MBWCampaignApp]
		budget: DF.Float
		channel: DF.Literal["Organic", "Paid Ads", "Referral", "Partner", "Event"]
		code_campaign: DF.Data
		creator: DF.Link | None
		day_end: DF.Date | None
		day_start: DF.Date
		description: DF.LongText | None
		name_campaign: DF.Data
		status: DF.Literal["Active", "Unactive", "Disable"]
	# end: auto-generated types
	
	def before_save(self):
		if not self.creator:
			self.creator = frappe.session.user
