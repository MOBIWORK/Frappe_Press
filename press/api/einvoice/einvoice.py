import frappe
from frappe import _
from frappe.utils import parse_json
import json
from press.api.einvoice.handle_einvoice import (
    handle_einvoice_from_supplier,
    lay_link_hoa_don_pdf_file,
    lay_link_04ss_pdf_file,
    handle_retry_einvoice
)

from press.api.einvoice.common import (
    find_name_replace_invoice
)

@frappe.whitelist()
def create_einvoice(name):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    invoice = frappe.db.get_value('Invoice', name, [
                                  'custom_status_einvoice', 'docstatus'], as_dict=1)

    if not invoice or invoice.docstatus != 1:
        return {"code": 0, "msg": _("Unable to generate an EInvoice for this bill.")}

    if invoice.custom_status_einvoice not in ['Not created']:
        return {"code": 0, "msg": _("An EInvoice can only be created once.")}
    rs = handle_einvoice_from_supplier(name, 0)
    if rs:
        return {"code": 200, "msg": _("The system is processing the invoice creation request.")}
    else:
        return {"code": 0, "msg": _("An error occurred")}


@frappe.whitelist()
def sign_einvoice(name):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    invoice = frappe.db.get_value('Invoice', name, [
                                  'custom_status_einvoice'], as_dict=1)
    if not invoice:
        return {"code": 0, "msg": _("Unable to generate an EInvoice for this bill.")}
    if invoice.custom_status_einvoice != "Newly created":
        return {"code": 0, "msg": _("An EInvoice can only be signed once.")}

    rs = handle_einvoice_from_supplier(name, 1)
    if rs:
        return {"code": 200, "msg": _("The system is processing the invoice signing request.")}
    else:
        return {"code": 0, "msg": _("An error occurred")}


@frappe.whitelist()
def update_status_einvoice(name):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    rs = handle_einvoice_from_supplier(name, 3)
    if rs:
        return {"code": 200, "msg": _("The system is processing the invoice status update request.")}
    else:
        return {"code": 0, "msg": _("An error occurred")}


@frappe.whitelist()
def cancel_einvoice(name, **kwargs):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    invoice = frappe.db.get_value('Invoice', name, [
                                  'custom_status_einvoice', 'custom_tax_status_einvoice'], as_dict=1)
    if invoice.custom_status_einvoice != 'Issued' or invoice.custom_tax_status_einvoice != "Signed":
        return {"code": 0, "msg": _("Electronic invoices can only be revoked when their status is `Issued` and the tax authority status is `Signed`.")}
    rs = handle_einvoice_from_supplier(name, 2, kwargs)
    if rs:
        return {"code": 200, "msg": _("The system is processing the invoice revocation request.")}
    else:
        return {"code": 0, "msg": _("An error occurred")}


@frappe.whitelist()
def einvoice_replacement(name, **kwargs):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    invoice = frappe.db.get_value('Invoice', name, [
                                  'amended_from', 'docstatus'], as_dict=1)
    if not invoice or invoice.docstatus != 1:
        return {"code": 0, "msg": _("Unable to generate an EInvoice for this bill.")}

    invoice_id = find_name_replace_invoice(invoice.amended_from)
    invoice_replace = frappe.db.get_value('Invoice', invoice_id, [
        'custom_status_einvoice', 'custom_tax_status_einvoice'], as_dict=1)

    if not invoice_replace:
        msg = _("The invoice to be replaced does not exist.")
        return {"code": 0, "msg": msg}

    if not invoice_replace.custom_status_einvoice in ['Issued', 'Replacement'] or invoice_replace.custom_tax_status_einvoice != "Signed":
        msg = _(
            """A replacement invoice for the invoice {0} can only be created when the electronic invoice is in the status `Issued/Replacement` and the tax authority status is `Signed`.""")
        link = "<a href='/app/sales-invoice/{0}'>{0}</a>".format(invoice_id)
        msg = msg.format(link)
        return {"code": 0, "msg": msg}

    rs = handle_einvoice_from_supplier(name, 5, kwargs)
    if rs:
        return {"code": 200, "msg": _("The system is processing the invoice replacement request.")}
    else:
        return {"code": 0, "msg": _("An error occurred")}


@frappe.whitelist()
def get_link_pdf_file(name, type_pdf):
    code = 0
    if type_pdf == "invoice":
        code, msg = lay_link_hoa_don_pdf_file(name)
    elif type_pdf == "cancellation_report":
        code, msg = lay_link_04ss_pdf_file(name)
    if code == 200:
        return {"code": code, "msg": _("Successful"), "data": {"link_pdf": msg}}
    return {"code": code, "msg": _("An error occurred")}


@frappe.whitelist()
def get_original_invoice(name, type_invoice=0):
    invoice_id = None
    invoice = frappe.db.get_value('Invoice', name, ['amended_from'], as_dict=1)
    if invoice:
        invoice_id = find_name_replace_invoice(invoice.amended_from)

    return invoice_id


@frappe.whitelist()
def retry_action_einvoice(data):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    try:
        data = json.loads(data or "{}")
        name_queue = data.get('name', '')
        doc_queue = frappe.db.get_value('MBW Detail EInvoice', name_queue, [
            'status', 'action'], as_dict=1)
        if not doc_queue or doc_queue.status != "Pending processing":
            return {"code": 0, "msg": _("Unable to process this record.")}

        # handle retry
        rs = handle_retry_einvoice(name_queue)
        if rs:
            action = _(doc_queue.action)
            msg = _(
                "The system is processing the request to redo the action `{0}`.").format(action)
            return {"code": 200, "msg": msg}
        else:
            return {"code": 0, "msg": _("An error occurred")}
    except Exception as ex:
        return {"code": 0, "msg": ex}


@frappe.whitelist()
def get_action_einvoice(name):
    invoice = frappe.db.get_value('Invoice', name, [
                                  'amended_from', 'custom_status_einvoice', 'custom_tax_status_einvoice', 'docstatus'], as_dict=1)
    data = {}

    if invoice and frappe.has_permission('Invoice', 'create'):
        data = {
            "create_ei": False,
            "replace_ei": False,
            "update_status_ei": False,
            "adjust_ei": False,
            "cancel_ei": False,
            "sign_ei": False,
            "cancel": True,
            "amend": False
        }
        queue_actions = {
            'Newly created': 'Create invoice',
            'Pending issuance': 'Create invoice',
            'Pending revocation': 'Revoke invoice',
            'Pending adjustment': 'Create invoice',
            'Pending replacement': 'Create invoice'
        }

        if invoice.docstatus != 0 and queue_actions.get(invoice.custom_status_einvoice):
            queue_create = frappe.get_all("MBW Detail EInvoice",
                                          fields=['idx'],
                                          filters={'parent': name, 'action': queue_actions[invoice.custom_status_einvoice], 'status': 'Successful'}, order_by="idx desc", limit=1)
            queue_sign = frappe.get_all("MBW Detail EInvoice",
                                        fields=['idx'],
                                        filters={'parent': name, 'action': 'Sign invoice', 'status': ('in', ['Pending processing', 'Successful'])}, order_by="idx desc", limit=1)
            if queue_create and not queue_sign:
                data['sign_ei'] = True

        if invoice.docstatus == 2:
            if (invoice.custom_status_einvoice in ["Replacement", "Issued"] and invoice.custom_tax_status_einvoice == "Signed") or invoice.custom_status_einvoice == "Not created":
                data['amend'] = True
        elif invoice.docstatus == 1:
            if invoice.custom_status_einvoice in ['Pending adjustment', 'Adjustment', 'Adjusted']:
                data['cancel'] = False

            if invoice.custom_status_einvoice == "Issued" and invoice.custom_tax_status_einvoice == "Signed":
                data['cancel_ei'] = True

            if invoice.custom_status_einvoice != "Not created":
                data['update_status_ei'] = True
            else:
                amended_from = find_name_replace_invoice(
                    invoice.amended_from)
                if amended_from:
                    data['replace_ei'] = True
                else:
                    data['create_ei'] = True

    return data


@frappe.whitelist()
def create_multiple_einvoice(names):
    if not frappe.has_permission('Invoice', 'create'):
        return {"code": 0, "msg": _("No permission to create.")}

    try:
        names = parse_json(names or '[]')
        for name in names:
            invoice = frappe.db.get_value('Invoice', name, [
                'amended_from', 'custom_status_einvoice', 'docstatus'], as_dict=1)

            if invoice and invoice.docstatus == 1 and invoice.custom_status_einvoice == "Not created":
                amended_from = find_name_replace_invoice(
                    invoice.amended_from)
                if not amended_from:
                    handle_einvoice_from_supplier(name, 0)

        return {"code": 200, "msg": _("The system is processing the invoice creation request.")}
    except Exception as ex:
        return {"code": 0, "msg": ex}