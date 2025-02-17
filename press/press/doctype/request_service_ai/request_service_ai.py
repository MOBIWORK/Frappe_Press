# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RequestServiceAI(Document):
    def validate(self):
        if not self.vat:
            vat_percentage = frappe.db.get_single_value(
                "Press Settings", "vat_percentage") or 0
            self.vat = vat_percentage

        amount = self.processing_unit * self.unit_price
        amount_vat = amount * self.vat / 100
        self.amount = round(amount + amount_vat, 2)
