import frappe
from frappe import _

def get_context(context):
    context.no_cache = True
    args = frappe.request.args
    lang = args.get('lang', 'vi')
    context.lang = lang
    return context