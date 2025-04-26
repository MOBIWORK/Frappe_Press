# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url
from press.api.language import get_language_from_team

class PartnerApprovalRequest(Document):
    def before_insert(self):
        self.key = frappe.generate_hash(15)

    def after_insert(self):
        if self.send_mail:
            self.send_approval_request_email()

    def send_approval_request_email(self):
        email = frappe.db.get_value("Team", self.partner, "user")
        customer = frappe.db.get_value("Team", self.requested_by, "user")
        
        lang = get_language_from_team(self.partner)
        lang = lang if lang in ['vi', 'en'] else 'vi'

        link = get_url(
            f"/api/method/press.api.account.approve_partner_request?key={self.key}"
        )
        pre_subject = "[MBWCloud] - "
        subject = pre_subject + _('Partner Approval Request', lang)

        # get language template
        template = 'partner_approval'
        template = f"{lang}_{template}"
        
        frappe.sendmail(
            subject=subject,
            recipients=email,
            template=template,
            args={"link": link, "user": customer, "partner": email},
            now=True,
        )
