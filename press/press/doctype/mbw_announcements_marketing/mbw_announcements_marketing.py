# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWAnnouncementsMarketing(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from press.press.doctype.mbw_announcements_marketing_app.mbw_announcements_marketing_app import MBWAnnouncementsMarketingApp
		from press.press.doctype.mbw_announcements_marketing_sites.mbw_announcements_marketing_sites import MBWAnnouncementsMarketingSites

		app: DF.Table[MBWAnnouncementsMarketingApp]
		content: DF.HTMLEditor | None
		day_end: DF.Datetime | None
		day_start: DF.Datetime
		name_announcement: DF.Data | None
		priority: DF.Int
		site: DF.Table[MBWAnnouncementsMarketingSites]
		status: DF.Literal["Running", "Not yet scheduled", "Finished", "Hidden"]
		type_announcement: DF.Literal["New Features", "Maintenance", "Promotions/Vouchers", "News", "Other"]
		type_show: DF.Literal["Marquee", "Modal"]
	# end: auto-generated types
	pass
