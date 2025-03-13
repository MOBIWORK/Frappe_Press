import frappe
from frappe import _
import json
import requests
from datetime import datetime
from frappe.utils import flt, rounded

from press.api.einvoice.common import (
    calc_retry_number,
    encrypt_base64,
    decrypt_base64,
    add_queue_log_ei,
    get_language_invoice,
)


def call_api_ei_bkav(ei_company, data):
    try:
        ei_settings = frappe.get_single('MBW EInvoice Settings')
        encrypted_data = encrypt_base64(data)
        partner_guid = ei_company.partner_guid_bkav

        if ei_company.environment_type == 'Production':
            url = ei_settings.api_url_bkav
        else:
            url = ei_settings.api_url_bkav_dev

        # send data to webservice
        payload = json.dumps({
            "partnerGUID": partner_guid,
            "CommandData": encrypted_data
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response and response.status_code != 200:
            frappe.log_error(
                'press.api.einvoice.bkav_einvoice.call_api_ei_bkav', response.text)
        return response
    except requests.exceptions.ConnectionError:
        frappe.log_error(
            'press.api.einvoice.bkav_einvoice.call_api_ei_bkav', 'Network error: Unable to connect to the server.')
        return frappe._dict({
            "status_code": -1,
            'msg': 'Network error: Unable to connect to the server.'
        })
    except requests.exceptions.Timeout:
        frappe.log_error(
            'press.api.einvoice.bkav_einvoice.call_api_ei_bkav', 'Request timed out.')
        return frappe._dict({
            "status_code": 599,
            'msg': 'Request timed out.'
        })
    except Exception as e:
        frappe.log_error(
            'press.api.einvoice.bkav_einvoice.call_api_ei_bkav', e)
        return frappe._dict({
            "status_code": 0,
            'msg': str(e)
        })


def xu_ly_hoa_don_bkav_ehoadon(invoice_id, process_type=0, info={}):
    """
    Chu thich
    * process_type = 0: tao hoa don va cap so hoa don
    * process_type = 1: dieu chinh hoa don
    * process_type = 2: thay the hoa don
    """

    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        invoice_no = 0
        invoice_form = ei_company.invoice_form_bkav or ""
        invoice_serial = ei_company.invoice_serial_bkav or ""
        invoice_type = {
            "Value-added tax invoice": 1
        }
        invoice_type_id = invoice_type.get(ei_company.invoice_type, 1)

        team = frappe.db.get_value(
            'Team', invoice.team, ['billing_address'], as_dict=1)

        address = None
        if team and team.billing_address:
            address = frappe.db.get_value('Address', team.billing_address, [
                'address_line1', 'email_id', 'phone', 'tax_code'], as_dict=1)

        taxes = {
            '0': 1,
            '5': 2,
            '8': 9,
            '10': 3
        }
        items = []
        discount_allocation = 0
        
        vat = invoice.vat or 0
        str_tax = str(vat).split('.')
        if str_tax[0] not in ['0', '5', '8', '10'] or (len(str_tax) == 2 and str_tax[1] != '0'):
            msg = _("Tax {0}% is invalid. Valid tax rates are 0% | 5% | 8% | 10%.").format(
                vat, get_language_invoice(invoice_id))
            return 0, msg

        tax_rate = int(vat)
        tax_rate_id = taxes.get(str(tax_rate))
        invoice_discount = sum([(d.amount or 0) for d in invoice.discounts])
        items_discount = sum([(item.discount or 0) for item in invoice.items])
        total_after_apply_items_discount = invoice.total_before_discount - items_discount
        for item in invoice.items:
            # calc amount
            qty = item.quantity
            amount = rounded(item.rate * qty, 2)
            discount_amount = item.discount
            amount_after_discount = amount - discount_amount

            # giam gia va tinh thue
            if item.idx == invoice.items[-1].idx:
                discount_amount_invoice = invoice_discount - discount_allocation
            else:
                discount_amount_invoice = amount_after_discount / \
                    total_after_apply_items_discount * invoice_discount
            discount_amount = discount_amount + discount_amount_invoice
            amount_after_discount = amount - discount_amount
            tax_amount = round(
                tax_rate / 100 * amount_after_discount)

            # Discount has been allocated
            discount_allocation += discount_amount_invoice

            item_data = {
                "ItemTypeID": 0,
                "IsDiscount": False,
                "ItemCode": item.item_code,
                "ItemName": item.item_name,
                "UnitName": item.unit,
                "Qty": qty,
                "Price": item.rate,
                "Amount": amount,
                "TaxRateID": tax_rate_id,
                "TaxRate": tax_rate,
                "TaxAmount": tax_amount,
                "DiscountRate": 0,
                "DiscountAmount": round(discount_amount),
                "UserDefineDetails": ""
            }
            if process_type == 2:
                item_data['IsIncrease'] = False

            items.append(item_data)
        
        address_line = []
        if address:
            if address.address_line1:
                address_line.append(address.address_line1)
            if address.county:
                address_line.append(address.county)
            if address.city:
                address_line.append(address.city)
        address_line = ", ".join(address_line) or ""
        
        data_invoice = {
            "InvoiceTypeID": invoice_type_id,
            "InvoiceDate": invoice.payment_date.strftime('%Y-%m-%d'),
            "BuyerName": invoice.customer_name,
            "BuyerTaxCode": address.tax_code if address else "",
            "BuyerUnitName": invoice.customer_name,
            "BuyerAddress": address_line,
            "BuyerBankAccount": "",
            "PayMethodID": 3,
            "ReceiveTypeID": 3,
            "ReceiverEmail": address.email_id if address else "",
            "ReceiverMobile": address.phone if address else "",
            "ReceiverAddress": address_line,
            "ReceiverName": invoice.customer_name,
            "Note": "Tạo từ OEVCloud",
            "BillCode": "",
            "CurrencyID": invoice.currency,
            "ExchangeRate": 1.0,
            "InvoiceForm": invoice_form,
            "InvoiceSerial": invoice_serial,
            "InvoiceNo": invoice_no,
            "OriginalInvoiceIdentify": ""
        }

        if process_type == 0:
            CmdType = 111
        elif process_type == 1:
            CmdType = 124
            data_adjustment = frappe.db.get_value('MBW Detail EInvoice', {
                'parent': invoice.custom_adjustment_einvoice_for, 'action': 'Create invoice', 'status': 'Successful'},
                ['json_data'])
            if not data_adjustment:
                return 0, _("Unable to create an adjustment electronic invoice for this invoice.", get_language_invoice(invoice_id))
            data_adjustment = json.loads(data_adjustment)
            OriginalInvoiceIdentify = f"[{data_adjustment.get('InvoiceForm')}]_[{data_adjustment.get('InvoiceSerial')}]_[{data_adjustment.get('InvoiceNo')}]"

            data_invoice['OriginalInvoiceIdentify'] = OriginalInvoiceIdentify
            data_invoice['Reason'] = info.get('reason', '')
        elif process_type == 2:
            CmdType = 123
            data_replacement = frappe.db.get_value('MBW Detail EInvoice', {
                'parent': invoice.custom_replacement_einvoice_for, 'action': 'Create invoice', 'status': 'Successful'},
                ['json_data'])
            if not data_replacement:
                return 0, _("Unable to create a replacement electronic invoice for this invoice.", get_language_invoice(invoice_id))
            data_replacement = json.loads(data_replacement)
            OriginalInvoiceIdentify = f"[{data_replacement.get('InvoiceForm')}]_[{data_replacement.get('InvoiceSerial')}]_[{data_replacement.get('InvoiceNo')}]"

            data_invoice['OriginalInvoiceIdentify'] = OriginalInvoiceIdentify
            data_invoice['Reason'] = info.get('reason', '')

        ei_data = {
            "CmdType": CmdType,
            "CommandObject": [
                {
                    "Invoice": data_invoice,
                    "ListInvoiceDetailsWS": items,
                    "PartnerInvoiceStringID": invoice.name
                }
            ]
        }
        
        # frappe.log_error(message=json.dumps(ei_data),title='xu_ly_hoa_don_bkav_ehoadon')

        # send data to webservice
        # === xy ly hoa don
        response = call_api_ei_bkav(ei_company, ei_data)
        if response.status_code == 200:
            resp = json.loads(response.text)
            return 200, resp
        else:
            return response.status_code, _("Unable to send data to the electronic invoice service.", get_language_invoice(invoice_id))
    except Exception as ex:
        return 0, str(ex)


def yc_thu_hoi_hoa_don_bkav_ehoadon(invoice_id, info={}):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        # === huy hoa don
        ei_data = {
            "CmdType": 202,
            "CommandObject": [
                {
                    "Invoice": {
                        "InvoiceTypeID": 1,
                        "Reason": info.get('reason', '')
                    },
                    "PartnerInvoiceStringID": invoice_id
                }

            ]
        }
        response = call_api_ei_bkav(ei_company, ei_data)
        if response.status_code == 200:
            resp = json.loads(response.text)
            return 200, resp
        else:
            return response.status_code, _("Unable to send data to the electronic invoice service.", get_language_invoice(invoice_id))
    except Exception as ex:
        return 0, str(ex)


def lay_trang_thai_hoa_don_bkav_ehoadon(invoice_id):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        json_data = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': 'Create invoice', 'status': 'Successful'}, ['json_data'])

        if not json_data:
            return 0, _("The data returned when creating the EInvoice does not exist.", get_language_invoice(invoice_id))

        # === lay thong tin trang thai
        json_data = json.loads(json_data)

        ei_data = {
            "CmdType": 850,
            "CommandObject": json_data.get('InvoiceGUID')
        }

        response = call_api_ei_bkav(ei_company, ei_data)
        if response.status_code == 200:
            resp = json.loads(response.text)
            return 200, resp
        else:
            return response.status_code, _("Unable to send data to the electronic invoice service.", get_language_invoice(invoice_id))
    except Exception as ex:
        return 0, str(ex)


def lay_link_hd_pdf_file_bkav_ehoadon(invoice_id):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        if invoice.custom_status_einvoice in ['Not created']:
            return 0, _("This invoice does not have a PDF file link for the EInvoice.", get_language_invoice(invoice_id))

        # === lay thong tin trang thai
        ei_data = {
            "CmdType": 816,
            "CommandObject": [{
                "PartnerInvoiceStringID": invoice.name
            }]
        }

        response = call_api_ei_bkav(ei_company, ei_data)
        if response.status_code == 200:
            resp = json.loads(response.text)
            return 200, resp
        else:
            return response.status_code, _("Unable to send data to the electronic invoice service.", get_language_invoice(invoice_id))
    except Exception as ex:
        return 0, str(ex)


def lay_link_04ss_pdf_file_bkav_ehoadon(invoice_id):
    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        if invoice.custom_status_einvoice not in ['Revoked', 'Pending revocation']:
            return 0, _("This invoice does not have a PDF file link for the revocation report.", get_language_invoice(invoice_id))

        # === lay thong tin trang thai
        ei_data = {
            "CmdType": 817,
            "CommandObject": [{
                "PartnerInvoiceStringID": invoice_id
            }]
        }

        response = call_api_ei_bkav(ei_company, ei_data)
        if response.status_code == 200:
            resp = json.loads(response.text)
            return 200, resp
        else:
            return response.status_code, _("Unable to send data to the electronic invoice service.", get_language_invoice(invoice_id))
    except Exception as ex:
        return 0, str(ex)


def yc_ky_hoa_don_bkav_ehoadon(invoice_id):
    from press.api.einvoice.handle_einvoice import handle_einvoice_from_supplier

    try:
        invoice = frappe.get_doc('Invoice', invoice_id)
        action = 'Sign invoice'
        ei_company = frappe.db.get_value('MBW EInvoice Company', {'einvoice_provider': invoice.custom_einvoice_supplier, 'environment_type': invoice.custom_env_type_einvoice}, ['*'], as_dict=1)

        data_queue = {}
        check_retry = False

        json_data = frappe.db.get_value('MBW Detail EInvoice', {
            'parent': invoice_id, 'action': 'Create invoice', 'status': 'Successful'}, ['json_data'])

        code = 0
        if not json_data:
            msg = _("The data returned when creating the EInvoice does not exist.",
                    get_language_invoice(invoice_id))
        else:
            json_data = json.loads(json_data)
            ei_data = {
                "CmdType": 205,
                "CommandObject": json_data.get('InvoiceGUID')
            }

            response = call_api_ei_bkav(ei_company, ei_data)

            if response.status_code == 200:
                resp = json.loads(response.text)
                d = resp.get('d')
                try:
                    decrypt_data = json.loads(decrypt_base64(d))
                    obj = decrypt_data.get('Object')
                    if decrypt_data.get('Status') == 0:
                        code = 200
                    resp['d'] = decrypt_data
                    msg = str(resp)
                except Exception as ex:
                    msg = str(ex)
            else:
                code = response.status_code
                msg = _("Unable to sign the invoice at this time.",
                        get_language_invoice(invoice_id))
                if code in [-1, 599]:
                    check_retry = True

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
                frappe.enqueue(yc_ky_hoa_don_bkav_ehoadon,
                               invoice_id=invoice_id)
        else:
            # cap nhat thong tin hoa don
            handle_einvoice_from_supplier(invoice_id, 3)

        # refresh form
        if invoice.docstatus == 1:
            invoice.reload()
            invoice.save(ignore_permissions=True)
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(),
                         'press.api.einvoice.bkav_einvoice.yc_ky_hoa_don_bkav_ehoadon')


def ghi_log_va_ky_HD_bkav(invoice_id):
    # add log
    data_more = {
        'action': 'Sign invoice'
    }
    add_queue_log_ei(invoice_id, data_more)
    # yeu cau phat hanh hoa don
    frappe.enqueue(yc_ky_hoa_don_bkav_ehoadon,
                   invoice_id=invoice_id)