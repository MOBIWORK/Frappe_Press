# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt


import frappe


@frappe.whitelist()
def all():
    payments = frappe.get_all(
        "Payment", fields=["name"], filters={"user": frappe.session.user}
    )
    return payments


@frappe.whitelist(allow_guest=True)
def webhook_payment(**data):
    print(data)
    return "done"
