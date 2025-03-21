# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
from frappe import _
from press.api.site import get_domain
from press.utils import get_country_info

def get_context(context):
    context.no_cache = True
    args = frappe.request.args
    lang = args.get('lang', 'vi')
    context.lang = lang
    domain = frappe.db.get_value("Press Settings", "Press Settings", ["domain"])
    context.domain = domain
    country_info = get_country_info() or {}
    country_name = country_info.get("country")
    context.country_name = (
        country_name if frappe.db.exists("Country", country_name) else ""
    )
    return context
