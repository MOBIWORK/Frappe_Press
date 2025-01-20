# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
from press.api.site import get_domain


def get_context(context):
    domain = frappe.db.get_value("Press Settings", "Press Settings", ["domain"])
    context.domain = domain
    return context
