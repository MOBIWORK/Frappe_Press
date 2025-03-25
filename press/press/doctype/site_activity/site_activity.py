# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from press.api.language import get_language_from_team


class SiteActivity(Document):
    def after_insert(self):
        if self.action == "Login as Administrator" and self.reason:
            d = frappe.get_all("Site", {"name": self.site}, ["notify_email", "team"])[0]
            recipient = d.notify_email or frappe.get_doc("Team", d.team).user
            if recipient:
                team = frappe.get_doc("Team", d.team)
                lang = get_language_from_team(d.team)
                lang = lang if lang in ['vi', 'en'] else 'vi'

                pre_subject = "[EOVCloud] - "
                subject = pre_subject + _('Administrator login to your site', lang)

                # get language template
                template = "admin_login"
                template = f"{lang}_{template}"

                team.notify_with_email(
                    [recipient],
                    subject=subject,
                    template=template,
                    args={"site": self.site, "user": self.owner, "reason": self.reason},
                    reference_doctype=self.doctype,
                    reference_name=self.name,
                    now=True,
                )


def log_site_activity(site, action, reason=None):
    return frappe.get_doc(
        {"doctype": "Site Activity", "site": site, "action": action, "reason": reason}
    ).insert()
