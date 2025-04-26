import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def get_status(**kwargs):
    lang = kwargs.get('lang') or 'vi'
    site_name = kwargs.get('site_name')
    if not site_name:
        frappe.throw(_("Site name is required", lang))
    if not frappe.db.exists("Site", site_name):
        frappe.throw(_("Site name not found", lang))
    
    status = frappe.db.get_value("Site", site_name, "status") or "Pending"
    
    return {
        "site_name": site_name,
        "status": status,
    }

def get_domain_setup(app_a):
    domain = frappe.get_value("Linked Applications", {'app_a': app_a}, ['domain'])
    return domain