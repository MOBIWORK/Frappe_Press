import frappe
from frappe import _
import base64
import json
from datetime import datetime

LANGUAGE_INVOICE = {
    "Vietnamese": "vi",
    "English": "en"
}

def get_language_invoice(invoice_id):
    invoice = frappe.db.get_value('Invoice', invoice_id, ['custom_einvoice_supplier', 'custom_env_type_einvoice'], as_dict=1)
    if not invoice:
        return ''

    ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['language'], as_dict=1)
    if not ei_company:
        return ''

    return LANGUAGE_INVOICE.get(ei_company.language, 'vi')


def encrypt_base64(data):
    # Bước 1: Chuyển đổi dữ liệu thành chuỗi JSON
    json_string = json.dumps(data)
    # Bước 2: Chuyển chuỗi thành byte
    data_bytes = json_string.encode('utf-8')
    # Bước 3: Mã hóa các byte trong Base64
    encode_base64 = base64.b64encode(data_bytes)

    return encode_base64.decode('utf-8')


def decrypt_base64(encrypted_base64):
    encrypted_data = base64.b64decode(encrypted_base64)
    return encrypted_data.decode('utf-8')


def find_name_replace_invoice(amended_from):
    if frappe.db.exists("Invoice", amended_from):
        invoice = frappe.db.get_value('Invoice', amended_from, [
            'amended_from', 'custom_status_einvoice', 'custom_tax_status_einvoice'], as_dict=1)
        check_exists = False
        if invoice.custom_status_einvoice in ["Issued", "Replacement"] and invoice.custom_tax_status_einvoice == "Signed":
            check_exists = True
        if check_exists:
            return amended_from
        else:
            if invoice.amended_from:
                return find_name_replace_invoice(invoice.amended_from)
    return None


def calc_retry_number(invoice_id, action):
    doc_retry = frappe.get_all("MBW Detail EInvoice",
                               fields=['retry_num', 'idx'],
                               filters={'parent': invoice_id, 'action': action, 'is_retry': 1, 'status': 'Failed'}, order_by="idx desc", limit=1)
    doc_no_retry = frappe.get_all("MBW Detail EInvoice",
                                  fields=['retry_num', 'idx'],
                                  filters={'parent': invoice_id, 'action': action, 'is_retry': 0}, order_by="idx desc", limit=1)
    if doc_retry:
        if not doc_no_retry or (doc_no_retry and doc_retry[0].idx > doc_no_retry[0].idx):
            return (doc_retry[0].retry_num or 0) + 1
    return 1


def set_config_ei_in_invoice(invoice_id):
    """
        - Cau hinh hoa don dien tu cho hoa don ban dau
    """
    invoice = frappe.db.get_value('Invoice', invoice_id,
                                  ['custom_einvoice_supplier', 'custom_env_type_einvoice', 'custom_tax_code', 'amended_from'], as_dict=1)
    parent_id = None
    supplier = invoice.custom_einvoice_supplier or ''
    environment_type = invoice.custom_env_type_einvoice or ''
    custom_tax_code = invoice.custom_tax_code or ''

    if not supplier or not environment_type:
        if invoice.amended_from:
            parent_id = invoice.custom_replacement_einvoice_for

        if not parent_id:
            ei_company = frappe.db.get_value('MBW EInvoice Company', {'is_active': 1}, ['einvoice_provider', 'environment_type', 'tax_code'], as_dict=1)
            if ei_company:
                supplier = ei_company.einvoice_provider
                environment_type = ei_company.environment_type
                custom_tax_code = ei_company.tax_code
        else:
            invoice_parent = frappe.db.get_value('Invoice', parent_id,
                                                 ['custom_einvoice_supplier', 'custom_env_type_einvoice', 'custom_tax_code'], as_dict=1)
            supplier = invoice_parent.custom_einvoice_supplier
            environment_type = invoice_parent.custom_env_type_einvoice
            custom_tax_code = invoice_parent.custom_tax_code or ''

        frappe.db.set_value('Invoice', invoice_id, {
            'custom_einvoice_supplier': supplier,
            'custom_env_type_einvoice': environment_type,
            'custom_tax_code': custom_tax_code
        })


def add_queue_log_ei(invoice_id, data_more={}):
    set_config_ei_in_invoice(invoice_id)
    invoice = frappe.db.get_value('Invoice', invoice_id,
                                  ['custom_einvoice_supplier', 'docstatus'], as_dict=1)
    idx = frappe.db.count('MBW Detail EInvoice', {'parent': invoice_id}) + 1
    data_insert = {
        'doctype': 'MBW Detail EInvoice',
        'parentfield': 'custom_queue_einvoice',
        'parenttype': 'Invoice',
        'parent': invoice_id,
        'supplier': invoice.custom_einvoice_supplier or '',
        'start_time': datetime.now(),
        'idx': idx
    }
    for x, y in data_more.items():
        data_insert[x] = y

    doc_queue = frappe.get_doc(data_insert)
    doc_queue.flags.ignore_permissions = True
    doc_queue.insert()
    doc_queue.submit()

    if invoice.docstatus == 1:
        invoice = frappe.get_doc('Invoice', invoice_id)
        invoice.save(ignore_permissions=True)
    elif invoice.docstatus == 2:
        doc_queue.cancel()