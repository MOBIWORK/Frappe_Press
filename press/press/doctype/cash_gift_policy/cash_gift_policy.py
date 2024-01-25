# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CashGiftPolicy(Document):
    pass
    # def after_insert(self):
    #     self.publish_created()

    # def publish_created(self):
    #     frappe.publish_realtime(
    #         "press_job_balance", {}
    #     )
