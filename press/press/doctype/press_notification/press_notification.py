# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PressNotification(Document):
    def after_insert(self):
        if frappe.local.dev_server:
            return
        
        user = frappe.db.get_value("Team", self.team, "user")
        if user == "Administrator":
            return

        if self.type == "Bench Deploy":
            self.send_bench_deploy_failed(user)

    def send_bench_deploy_failed(self, user: str):
        group_name = frappe.db.get_value(
            "Deploy Candidate", self.document_name, "group")
        rg_title = frappe.db.get_value(
            "Release Group", group_name, "title")

        lang = frappe.db.get_value('User', user, 'language')
        lang = lang if lang in ['vi', 'en'] else 'vi'
        
        pre_subject = "[MBWCloud] - "
        subject = pre_subject + _('Bench Deploy Failed - {0}', lang).format(rg_title)
        
        # get language template
        template = 'bench_deploy_failure'
        template = f"{lang}_{template}"
        
        frappe.sendmail(
            recipients=[user],
            subject=subject,
            template=template,
            args={
                "message": self.message,
                "link": f"dashboard/benches/{group_name}/deploys/{self.document_name}",
            },
        )


def create_new_notification(team, type, document_type, document_name, message):
    if not frappe.db.exists("Press Notification", {"document_name": document_name}):
        frappe.get_doc(
            {
                "doctype": "Press Notification",
                "team": team,
                "type": type,
                "document_type": document_type,
                "document_name": document_name,
                "message": message,
            }
        ).insert()
        frappe.publish_realtime("press_notification", {"team": team})
