import frappe
from frappe import _
import json
from datetime import datetime
from frappe.utils import parse_json

from press.api.einvoice.common import (
    find_name_replace_invoice,
    calc_retry_number,
    add_queue_log_ei,
    decrypt_base64,
    get_language_invoice
)
from press.api.einvoice.bkav_einvoice import (
    xu_ly_hoa_don_bkav_ehoadon,
    yc_thu_hoi_hoa_don_bkav_ehoadon,
    lay_trang_thai_hoa_don_bkav_ehoadon,
    lay_link_hd_pdf_file_bkav_ehoadon,
    lay_link_04ss_pdf_file_bkav_ehoadon,
    ghi_log_va_ky_HD_bkav
)
from press.press.doctype.invoice.invoice import validate_item_invoice


def handle_einvoice_from_supplier(invoice_id, action_ei=0, data={}):
    validate_item_invoice(invoice_id)
    """
    Chu thich:
    * action_ei = 0: Tao hoa don
    * action_ei = 1: Ky hoa don
    * action_ei = 2: Thu hoi hoa don
    * action_ei = 3: Cap nhat trang thai
    * action_ei = 4: Dieu chinh hoa don
    * action_ei = 5: Thay the hoa don
    """
    try:
        if action_ei == 0:
            check_exists = frappe.db.exists('MBW Detail EInvoice', {
                'parent': invoice_id, 'action': 'Create invoice', 'status': 'Pending processing'})
            if not check_exists:
                data_more = {
                    'action': "Create invoice"
                }
                add_queue_log_ei(invoice_id, data_more)
                # add queue
                frappe.enqueue(tao_hoa_don, invoice_id=invoice_id)
        elif action_ei == 1:
            check_exists = frappe.db.exists('MBW Detail EInvoice', {
                'parent': invoice_id, 'action': 'Sign invoice', 'status': 'Pending processing'})
            if not check_exists:
                ky_hoa_don(invoice_id)
        elif action_ei == 2:
            check_exists = frappe.db.exists('MBW Detail EInvoice', {
                'parent': invoice_id, 'action': 'Revoke invoice', 'status': 'Pending processing'})
            if not check_exists:
                data_more = {
                    'action': "Revoke invoice"
                }
                add_queue_log_ei(invoice_id, data_more)
                # add queue
                frappe.enqueue(thu_hoi_hoa_don_phat_hanh,
                               invoice_id=invoice_id, info=data)
        elif action_ei == 3:
            check_exists = frappe.db.exists('MBW Detail EInvoice', {
                'parent': invoice_id, 'action': 'Update status', 'status': 'Pending processing'})
            if not check_exists:
                data_more = {
                    'action': "Update status"
                }
                add_queue_log_ei(invoice_id, data_more)
                # add queue
                frappe.enqueue(cap_nhat_trang_thai_hoa_don,
                               invoice_id=invoice_id)
        elif action_ei == 4:
            pass
        elif action_ei == 5:
            check_exists = frappe.db.exists('MBW Detail EInvoice', {
                'parent': invoice_id, 'action': 'Create invoice', 'status': 'Pending processing'})
            if not check_exists:
                data_more = {
                    "action": "Create invoice",
                    "attached_data": json.dumps(data or {})
                }
                add_queue_log_ei(invoice_id, data_more)
                # add queue
                frappe.enqueue(thay_the_hoa_don,
                               invoice_id=invoice_id, info=data)
        return True
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.handle_einvoice_from_supplier')
        return False


def ky_hoa_don(invoice_id):
    invoice = frappe.db.get_value('Invoice', invoice_id, [
                                  'custom_einvoice_supplier'], as_dict=1)

    if invoice.custom_einvoice_supplier == "BKAV eHoadon":
        # ky hoa don
        ghi_log_va_ky_HD_bkav(invoice_id)


def handle_retry_einvoice(name):
    try:
        rs = True
        doc_queue = frappe.db.get_value('MBW Detail EInvoice', name, [
            'action', 'attached_data', 'parent'], as_dict=1)

        invoice = frappe.db.get_value('Invoice', doc_queue.parent, ['amended_from', 'custom_einvoice_supplier'], as_dict=1)

        attached_data = parse_json(doc_queue.attached_data or '{}')
        # cancel doc queue
        frappe.db.set_value('MBW Detail EInvoice', name, {
            'status': 'Cancelled',
            'end_time': datetime.now()
        })

        if doc_queue.action == "Create invoice":
            amended_from = find_name_replace_invoice(
                invoice.amended_from)
            if amended_from:
                rs = handle_einvoice_from_supplier(
                    doc_queue.parent, 5, attached_data)
            else:
                rs = handle_einvoice_from_supplier(doc_queue.parent, 0)
        elif doc_queue.action == "Sign invoice":
            ky_hoa_don(doc_queue.parent)
        elif doc_queue.action == "Update status":
            rs = handle_einvoice_from_supplier(doc_queue.parent, 3)
        elif doc_queue.action == "Revoke invoice":
            rs = handle_einvoice_from_supplier(
                doc_queue.parent, 2, attached_data)

        if rs:
            frappe.db.commit()
        else:
            frappe.db.rollback()

        return rs
    except Exception as ex:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(),
                         'mbw_einvoice.api.handle_einvoice.handle_retry_einvoice')
        return False


def check_ei_setting(invoice_id):
    invoice = frappe.db.get_value('Invoice', invoice_id, ['custom_einvoice_supplier', 'custom_env_type_einvoice'], as_dict=1)
    ei_settings = frappe.get_single('MBW EInvoice Settings')
    ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)
    messages_err = []
    code = 200

    if not ei_settings.enable_einvoice:
        msg = _(
            "Please configure the permission to create EInvoice in `{0}`.", get_language_invoice(invoice_id))
        link = """<a href="/app/mbw-einvoice-settings">MBW EInvoice Settings</a>"""
        msg = msg.format(link)
        code = 0
        messages_err.append(msg)

    if not ei_company:
        msg = _(
            "Please configure EInvoice information for the company `{0}` in `{1}`.", get_language_invoice(invoice_id))
        link = """<a href="/app/mbw-einvoice-company/view/list">MBW EInvoice Company</a>"""
        msg = msg.format('MBW', link)
        code = 0
        messages_err.append(msg)

    return code, str(messages_err)


def tao_hoa_don(invoice_id):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        data_queue = {}
        check_retry = False
        action = 'Create invoice'

        code, msg = check_ei_setting(invoice_id)
        if code == 200:
            if invoice.docstatus != 1:
                code = 0
                msg = _("Unable to generate an EInvoice for this bill.",
                        get_language_invoice(invoice_id))

        if code == 200:
            # handle invoice
            code = 0
            if invoice.custom_einvoice_supplier == "BKAV eHoadon":
                c, r = xu_ly_hoa_don_bkav_ehoadon(invoice_id, 0)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            obj = json.loads(obj)
                            rs_ei = obj[0]
                            if rs_ei.get('Status') == 0:
                                code = 200
                                json_data = json.dumps(rs_ei, indent=4)
                                data_queue['invoice_serial'] = rs_ei.get(
                                    'InvoiceSerial')
                                data_queue['invoice_form'] = rs_ei.get(
                                    'InvoiceForm')
                                data_queue['json_data'] = json_data
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
                else:
                    if c in [-1, 599]:
                        check_retry = True
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    invoice.custom_einvoice_supplier)

        status = 'Failed'
        if code == 200:
            status = 'Successful'

        data_queue['status'] = status
        data_queue['message_log'] = msg
        data_queue['end_time'] = datetime.now()

        queue_name = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': action, 'status': 'Pending processing'}, ['name'])
        if queue_name:
            frappe.db.set_value('MBW Detail EInvoice', queue_name, data_queue)
        else:
            data_queue['action'] = action
            add_queue_log_ei(invoice_id, data_queue)

        # buoc tiep theo cua nha cung cap
        if code == 200:
            ky_hoa_don(invoice_id)

        if check_retry:
            number_of_retries = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'number_of_retries')
            number_of_retries = number_of_retries or 0
            retry_number = calc_retry_number(invoice_id, action)
            if retry_number <= number_of_retries:
                data_more = {
                    'action': action,
                    'is_retry': 1,
                    'retry_num': retry_number,
                }
                add_queue_log_ei(invoice_id, data_more)
                # retry
                frappe.enqueue(tao_hoa_don,
                               invoice_id=invoice_id)
        # refresh form
        if invoice.docstatus == 1:
            invoice.reload()
            invoice.save(ignore_permissions=True)
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.tao_hoa_don')


def thu_hoi_hoa_don_phat_hanh(invoice_id, info={}):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        data_queue = {}
        check_retry = False
        action = 'Revoke invoice'

        code, msg = check_ei_setting(invoice_id)

        if code == 200:
            # handle invoice
            code = 0
            if invoice.custom_einvoice_supplier == "BKAV eHoadon":
                c, r = yc_thu_hoi_hoa_don_bkav_ehoadon(invoice_id, info)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            obj = json.loads(obj)
                            rs_ei = obj[0]
                            if rs_ei.get('Status') == 0:
                                code = 200
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
                else:
                    if c in [-1, 599]:
                        check_retry = True
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    invoice.custom_einvoice_supplier)

        status = 'Failed'
        if code == 200:
            status = 'Successful'

        data_queue['status'] = status
        data_queue['message_log'] = msg
        data_queue['end_time'] = datetime.now()

        queue_name = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': action, 'status': 'Pending processing'}, ['name'])
        if queue_name:
            frappe.db.set_value('MBW Detail EInvoice', queue_name, data_queue)
        else:
            data_queue['action'] = action
            add_queue_log_ei(invoice_id, data_queue)

        # buoc tiep theo cua nha cung cap
        if code == 200:
            ky_hoa_don(invoice_id)
        if check_retry:
            number_of_retries = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'number_of_retries')
            number_of_retries = number_of_retries or 0
            retry_number = calc_retry_number(invoice_id, action)
            if retry_number <= number_of_retries:
                data_more = {
                    'action': action,
                    'is_retry': 1,
                    'retry_num': retry_number,
                }
                add_queue_log_ei(invoice_id, data_more)
                # retry
                frappe.enqueue(thu_hoi_hoa_don_phat_hanh,
                               invoice_id=invoice_id, info=info)
        # refresh form
        if invoice.docstatus == 1:
            invoice.reload()
            invoice.save(ignore_permissions=True)
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.thu_hoi_hoa_don_phat_hanh')


def thay_the_hoa_don(invoice_id, info={}):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        replace_id = find_name_replace_invoice(invoice.amended_from)
        original_invoice = None
        data_queue = {}
        data_invoice = {}
        check_retry = False
        code = 0
        action = 'Create invoice'

        if replace_id:
            original_invoice = frappe.db.get_value('Invoice', replace_id,
                                                   ['custom_env_type_einvoice', 'custom_einvoice_supplier', 'custom_tax_code'], as_dict=1)
            data_invoice['custom_replacement_einvoice_for'] = replace_id
            data_invoice['custom_env_type_einvoice'] = original_invoice.custom_env_type_einvoice
            data_invoice['custom_einvoice_supplier'] = original_invoice.custom_einvoice_supplier
            data_invoice['custom_tax_code'] = original_invoice.custom_tax_code
            code, msg = check_ei_setting(replace_id)
        else:
            msg = _("Unable to create a replacement invoice for this invoice.",
                    get_language_invoice(invoice_id))

        if code == 200:
            if invoice.docstatus != 1:
                code = 0
                msg = _("Unable to generate an EInvoice for this bill.",
                        get_language_invoice(invoice_id))

        if code == 200:
            # update invoice
            frappe.db.set_value('Invoice', invoice_id, data_invoice)

            # handle invoice
            code = 0
            if original_invoice.custom_einvoice_supplier == "BKAV eHoadon":
                c, r = xu_ly_hoa_don_bkav_ehoadon(invoice_id, 2, info)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            obj = json.loads(obj)
                            rs_ei = obj[0]
                            if rs_ei.get('Status') == 0:
                                code = 200
                                json_data = json.dumps(rs_ei, indent=4)
                                data_queue['invoice_serial'] = rs_ei.get(
                                    'InvoiceSerial')
                                data_queue['invoice_form'] = rs_ei.get(
                                    'InvoiceForm')
                                data_queue['json_data'] = json_data
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
                else:
                    if c in [-1, 599]:
                        check_retry = True
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    original_invoice.custom_einvoice_supplier)

        status = 'Failed'
        if code == 200:
            status = 'Successful'

        data_queue['status'] = status
        data_queue['message_log'] = msg
        data_queue['end_time'] = datetime.now()

        queue_name = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': action, 'status': 'Pending processing'}, ['name'])
        if queue_name:
            frappe.db.set_value('MBW Detail EInvoice', queue_name, data_queue)
        else:
            data_queue['action'] = action
            add_queue_log_ei(invoice_id, data_queue)

        # buoc tiep theo cua nha cung cap
        if code == 200:
            ky_hoa_don(invoice_id)

        if check_retry:
            number_of_retries = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'number_of_retries')
            number_of_retries = number_of_retries or 0
            retry_number = calc_retry_number(invoice_id, action)
            if retry_number <= number_of_retries:
                data_more = {
                    'action': action,
                    'is_retry': 1,
                    'retry_num': retry_number,
                }
                add_queue_log_ei(invoice_id, data_more)
                # retry
                frappe.enqueue(thay_the_hoa_don,
                               invoice_id=invoice_id, info=info)
        # refresh form
        if invoice.docstatus == 1:
            invoice.reload()
            invoice.save(ignore_permissions=True)
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.thay_the_hoa_don')


def lay_link_hoa_don_pdf_file(invoice_id):
    link_pdf = None
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_settings = frappe.get_single('MBW EInvoice Settings')

        code, msg = check_ei_setting(invoice_id)

        if code == 200:
            # handle invoice
            code = 0
            if invoice.custom_einvoice_supplier == "BKAV eHoadon":
                if invoice.custom_env_type_einvoice == "Production":
                    link_web = ei_settings.link_web_bkav or ''
                else:
                    link_web = ei_settings.link_web_bkav_dev or ''

                c, r = lay_link_hd_pdf_file_bkav_ehoadon(invoice_id)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            obj = json.loads(obj)
                            rs_ei = obj[0]
                            if rs_ei.get('Status') == 0:
                                code = 200
                                link_pdf = link_web + rs_ei.get('MessLog')
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    invoice.custom_einvoice_supplier)

        if code == 0:
            data_err = {
                'name': invoice_id,
                'message_log': msg,
                'action': 'Lấy Link Hóa đơn File PDF',
                'supplier': invoice.custom_einvoice_supplier,
            }
            frappe.log_error(
                'press.api.einvoice.handle_einvoice.lay_link_hoa_don_pdf_file', json.dumps(data_err, indent=4))

        return code, msg if code == 0 else link_pdf
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.lay_link_hoa_don_pdf_file')


def lay_link_04ss_pdf_file(invoice_id):
    link_pdf = None
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_settings = frappe.get_single('MBW EInvoice Settings')

        code, msg = check_ei_setting(invoice_id)

        if code == 200:
            # handle invoice
            code = 0
            if invoice.custom_einvoice_supplier == "BKAV eHoadon":
                if invoice.custom_env_type_einvoice == "Production":
                    link_web = ei_settings.link_web_bkav or ''
                else:
                    link_web = ei_settings.link_web_bkav_dev or ''

                c, r = lay_link_04ss_pdf_file_bkav_ehoadon(invoice_id)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            obj = json.loads(obj)
                            rs_ei = obj[0]
                            if rs_ei.get('Status') == 0:
                                code = 200
                                link_pdf = link_web + rs_ei.get('MessLog')
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    invoice.custom_einvoice_supplier)

        if code == 0:
            data_err = {
                'name': invoice_id,
                'message_log': msg,
                'action': 'Lấy Link 04SS File PDF',
                'supplier': invoice.custom_einvoice_supplier,
            }
            frappe.log_error(
                'press.api.einvoice.handle_einvoice.lay_link_04ss_pdf_file', json.dumps(data_err, indent=4))

        return code, msg if code == 0 else link_pdf
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.lay_link_04ss_pdf_file')


def send_email_log(name_log, company, names_invoice=[]):
    config_company = frappe.db.get_value('MBW EInvoice Company', {'is_active': 1}, ['allow_send_email', 'language', 'recipient_email'], as_dict=1)
    if config_company and config_company.allow_send_email == 1 and config_company.recipient_email:
        recipient_email = config_company.recipient_email.strip()
        name_temp = None
        if config_company.language == "English":
            name_temp = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'er_email_template_en')
        else:
            name_temp = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'er_email_template_vi')

        if name_temp:
            email_template = frappe.get_doc('Email Template', name_temp)
            recipients = [recipient_email]
            html_names_invoice = ""
            for n in names_invoice:
                html_names_invoice += "<p>- {0}</p>".format(n)
            args = {'names_invoice': html_names_invoice}
            subject = email_template.subject
            if email_template.use_html:
                content = frappe.render_template(
                    email_template.response_html, args)
            else:
                content = frappe.render_template(email_template.response, args)

            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                content=content,
                now=False,
            )

            # update email log
            frappe.db.set_value('MBW EInvoice Email Log', name_log, {
                "recipient_email": recipient_email
            })


def update_email_log(name, invoice_id, is_err=False):
    try:
        doc = frappe.db.get_value('MBW EInvoice Email Log', name, [
            'num_of_invoices_reviewed', 'num_of_successful_invoices', 'num_of_failed_invoices', 'names_of_successful_invoices', 'names_of_failed_invoices', 'company'], as_dict=1, for_update=True)
        if doc:
            data_update = {}
            num_of_successful_invoices = doc.num_of_successful_invoices
            num_of_failed_invoices = doc.num_of_failed_invoices
            names_of_failed_invoices = parse_json(
                doc.names_of_failed_invoices or '[]')
            names_of_successful_invoices = parse_json(
                doc.names_of_successful_invoices or '[]')
            if is_err:
                num_of_failed_invoices += 1
                names_of_failed_invoices.append(invoice_id)
                data_update = {
                    'num_of_failed_invoices': num_of_failed_invoices,
                    'names_of_failed_invoices': json.dumps(names_of_failed_invoices)
                }
            else:
                num_of_successful_invoices += 1
                names_of_successful_invoices.append(invoice_id)
                data_update = {
                    'num_of_successful_invoices': num_of_successful_invoices,
                    'names_of_successful_invoices': json.dumps(names_of_successful_invoices)
                }

            frappe.db.set_value('MBW EInvoice Email Log', name, data_update)
            # Commit giao dịch để lưu thay đổi
            frappe.db.commit()

            # check and send email
            if doc.num_of_invoices_reviewed == (num_of_successful_invoices + num_of_failed_invoices) and num_of_failed_invoices > 0:
                send_email_log(name, doc.company, names_of_failed_invoices)
    except Exception as ex:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.update_email_log')


def kiem_tra_trang_thai_hoa_don():
    try:
        status_einvoice = ['Pending issuance', 'Pending revocation',
                           'Pending adjustment', 'Pending replacement']

        invoices = frappe.db.get_all('Invoice', filters=[['custom_status_einvoice', 'in', status_einvoice], ['docstatus', '=', 1]], pluck='name', limit=500)
        if len(invoices) > 0:
            # add email log
            doc_log = frappe.new_doc('MBW EInvoice Email Log')
            doc_log.company = 'MBW'
            doc_log.start_time = datetime.now()
            doc_log.num_of_invoices_reviewed = len(invoices)
            doc_log.flags.ignore_permissions = True
            doc_log.insert()

            for invoice_id in invoices:
                check_exists = frappe.db.exists('MBW Detail EInvoice', {
                    'parent': invoice_id, 'action': 'Update status', 'status': 'Pending processing'})
                if not check_exists:
                    data_more = {
                        'action': "Update status"
                    }
                    add_queue_log_ei(invoice_id, data_more)

                # add queue
                frappe.enqueue(cap_nhat_trang_thai_hoa_don,
                                invoice_id=invoice_id, email_log=doc_log.name)
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.kiem_tra_trang_thai_hoa_don')


def cap_nhat_trang_thai_hoa_don(invoice_id, email_log=None):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        data_invoice = {}
        data_queue = {}
        check_retry = False
        action = 'Update status'

        code, msg = check_ei_setting(invoice_id)
        if code == 200:
            code = 0
            d_status = {
                "1": "Newly created",
                "2": "Issued",
                "3": "Revoked",
                "5": "Pending replacement",
                "6": "Replacement",
                "7": "Pending adjustment",
                "8": "Adjustment",
                "9": "Replaced",
                "10": "Adjusted",
                "11": "Pending issuance",
                "12": "Not in use",
                "13": "Pending revocation",
            }
            if invoice.custom_einvoice_supplier == "BKAV eHoadon":
                d_tax_status = {
                    '0': '',
                    '32': 'Pending approval',
                    '33': 'Signed',
                    '34': 'Error',
                    '35': 'Error',
                    '36': 'Pending signature',
                    '37': 'Error',
                    '38': 'Error',
                    '39': 'Error',
                }

                c, r = lay_trang_thai_hoa_don_bkav_ehoadon(invoice_id)
                msg = str(r)
                if c == 200:
                    d = r.get('d')
                    try:
                        decrypt_data = json.loads(decrypt_base64(d))
                        obj = decrypt_data.get('Object')
                        if decrypt_data.get('Status') == 0:
                            code = 200
                            BkavStatus = str(obj.get('BkavStatus', ''))
                            TaxStatus = str(obj.get('TaxStatus', ''))
                            status_einvoice = d_status.get(BkavStatus, '')
                            tax_status = d_tax_status.get(TaxStatus, '')
                            if status_einvoice:
                                if BkavStatus in ["7", "8"]:
                                    # xu ly update hoa don dieu chinh goc
                                    adjust_id = invoice.custom_adjustment_einvoice_for
                                    if adjust_id:
                                        data_more = {
                                            'action': action
                                        }
                                        add_queue_log_ei(adjust_id, data_more)
                                        frappe.enqueue(cap_nhat_trang_thai_hoa_don,
                                                       invoice_id=adjust_id)
                                elif BkavStatus in ["5", "6"] and invoice.amended_from:
                                    # xu ly update hoa don thay the goc
                                    replace_id = invoice.custom_replacement_einvoice_for
                                    if replace_id:
                                        data_more = {
                                            'action': action
                                        }
                                        add_queue_log_ei(replace_id, data_more)
                                        frappe.enqueue(cap_nhat_trang_thai_hoa_don,
                                                       invoice_id=replace_id)
                            data_invoice['custom_status_einvoice'] = status_einvoice
                            data_invoice['custom_tax_status_einvoice'] = tax_status
                            data_queue['status_einvoice'] = status_einvoice
                            data_queue['tax_status_einvoice'] = tax_status
                        r['d'] = decrypt_data
                        msg = str(r)
                    except Exception as ex:
                        msg = str(ex)
                else:
                    if c in [-1, 599]:
                        check_retry = True
            else:
                msg = _("The system does not support the provider `{0}` yet.", get_language_invoice(invoice_id)).format(
                    invoice.custom_einvoice_supplier)

        status = 'Failed'
        is_err = True
        if code == 200:
            is_err = False
            status = 'Successful'

        data_queue['status'] = status
        data_queue['message_log'] = msg
        data_queue['end_time'] = datetime.now()

        queue_name = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': action, 'status': 'Pending processing'}, ['name'])
        if queue_name:
            frappe.db.set_value('MBW Detail EInvoice', queue_name, data_queue)
        else:
            data_queue['action'] = action
            add_queue_log_ei(invoice_id, data_queue)

        # update invoice
        frappe.db.set_value('Invoice', invoice_id, data_invoice)

        if check_retry:
            number_of_retries = frappe.db.get_single_value(
                'MBW EInvoice Settings', 'number_of_retries')
            number_of_retries = number_of_retries or 0
            retry_number = calc_retry_number(invoice_id, action)
            if retry_number <= number_of_retries:
                data_more = {
                    'action': action,
                    'is_retry': 1,
                    'retry_num': retry_number,
                }
                add_queue_log_ei(invoice_id, data_more)
                # retry
                frappe.enqueue(cap_nhat_trang_thai_hoa_don,
                               invoice_id=invoice_id)
        # refresh form
        if invoice.docstatus == 1:
            invoice.reload()
            invoice.save(ignore_permissions=True)

        if email_log:
            update_email_log(email_log, invoice_id, is_err=is_err)
    except Exception as ex:
        if email_log:
            update_email_log(email_log, invoice_id, is_err=True)
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.handle_einvoice.cap_nhat_trang_thai_hoa_don')