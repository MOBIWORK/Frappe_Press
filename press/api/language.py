import frappe
from frappe import _

@frappe.whitelist()
def get_language():
    language = frappe.db.get_value('User', frappe.session.user, 'language')
    if not language:
        language = 'vi'
        frappe.db.set_value('User', frappe.session.user, {
            'language': language
        })
    return language


@frappe.whitelist()
def change_language(lang):
    language = frappe.db.get_value('Language', lang, 'name')
    if language:
        frappe.db.set_value('User', frappe.session.user, {
            'language': lang
        })
        return lang
    else:
        frappe.throw(_('Language not found'))