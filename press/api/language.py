import frappe
from frappe import _
from frappe.translate import get_all_translations

def get_language_from_team(team):
	lang = 'vi'
	if team:
		user = frappe.db.get_value('Team', team, 'user')
		if user:
			lang = frappe.db.get_value('User', user, 'language') or lang
	return lang

@frappe.whitelist(allow_guest=True)
def get_language():
	lang = 'vi'
	if frappe.session.user != "Guest":
		language = frappe.db.get_value('User', frappe.session.user, 'language')
		lang = language or lang
		if not language:
			frappe.db.set_value('User', frappe.session.user, {
				'language': lang
			})
	return lang


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

@frappe.whitelist(allow_guest=True)
def get_translations(lang: str = None):
    if lang:
        language = lang
    else:
        if frappe.session.user != "Guest":
            language = frappe.db.get_value(
                "User", frappe.session.user, "language")
        else:
            language = frappe.db.get_single_value(
                "System Settings", "language")
    return get_all_translations(language)