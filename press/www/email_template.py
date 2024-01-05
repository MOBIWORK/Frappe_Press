import frappe


def get_context(context):
    content_email = ''
    name_email_template = frappe.db.get_value(
        "Press Settings", "Press Settings", "email_template_money_into_account"
    )
    if name_email_template:
        email_template = frappe.db.get_value('Email Template', name_email_template, [
            'subject', 'use_html', 'response_html', 'response'], as_dict=1)
        if email_template.use_html:
            content_email = email_template.response_html
        else:
            content_email = email_template.response

    context.rendered_email = content_email
    context.no_cache = 1
