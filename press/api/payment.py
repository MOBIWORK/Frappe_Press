# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt


import frappe
from press.utils import check_payos_settings
from payos import PayOS


@frappe.whitelist()
def all():
    payments = frappe.get_all(
        "Payment", fields=["name"], filters={"user": frappe.session.user}
    )
    return payments


@frappe.whitelist(allow_guest=True, methods=['POST'])
def webhook_payment(**webhookBody):
    doc_log = frappe.new_doc("PayOs Log")
    doc_log.webhook_body = str(webhookBody)
    doc_log.code = '1'

    try:
        payos_settings = check_payos_settings()
        data = webhookBody.get('data')
        if type(data) != dict:
            doc_log.message = 'Dữ liệu webhook không đúng định dạng.'
            doc_log.insert(ignore_permissions=True)
            return {
                'code': '1',
                'desc': 'Dữ liệu webhook không đúng định dạng.'
            }

        name = frappe.db.get_value(
            'Balance Transaction', {'order_code': data.get('orderCode')}, ['name'])
        if not payos_settings:
            doc_log.message = 'Vui lòng cấu hình đầy đủ thông tin PayOs trong Press Settings.'
            doc_log.insert(ignore_permissions=True)

            return {
                'code': '1',
                'desc': 'Vui lòng cấu hình đầy đủ thông tin PayOs trong Press Settings.'
            }

        if not name:
            doc_log.message = 'Không tìm thấy giao dịch.'
            doc_log.insert(ignore_permissions=True)

            return {
                'code': '1',
                'desc': 'Không tìm thấy giao dịch.'
            }

        payOS = PayOS(client_id=payos_settings.get('payos_client_id'), api_key=payos_settings.get(
            'payos_api_key'), checksum_key=payos_settings.get('payos_checksum_key'))

        webhookData = payOS.verifyPaymentWebhookData(webhookBody)

        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)
        if balance_transaction.docstatus != 0:
            doc_log.message = 'Giao dịch đã thanh toán hoặc hủy trước đó.'
            doc_log.insert(ignore_permissions=True)
            return {
                'code': '1',
                'desc': 'Giao dịch đã thanh toán hoặc hủy trước đó.'
            }

        balance_transaction.docstatus = 1
        balance_transaction.payos_payment_status = "PAID"
        balance_transaction.save(ignore_permissions=True)

        doc_log.code = '00'
        doc_log.message = 'Thanh toán thành công.'
        doc_log.insert(ignore_permissions=True)

        return {
            'code': '0',
            'desc': 'Thanh toán thành công.'
        }
    except Exception as ex:
        doc_log.code = '1'
        doc_log.message = str(ex)
        doc_log.insert(ignore_permissions=True)

        return {
            'code': '1',
            'desc': str(ex)
        }
