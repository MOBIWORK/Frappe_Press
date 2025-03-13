# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RequestServiceAI(Document):
    def validate(self):
        amount = self.processing_unit * self.unit_price
        amount_vat = amount * self.vat / 100
        self.amount = round(amount + amount_vat, 2)
