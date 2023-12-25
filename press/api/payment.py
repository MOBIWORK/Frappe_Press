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
    try:
        payos_settings = check_payos_settings()
        data = webhookBody.get('data')
        if type(data) != dict:
            return {
                'code': '1',
                'desc': 'Dữ liệu webhook không đúng định dạng.'
            }

        name = frappe.db.get_value(
            'Balance Transaction', {'order_code': data.get('orderCode')}, ['name'])
        if not payos_settings:
            return {
                'code': '1',
                'desc': 'Vui lòng cấu hình đầy đủ thông tin PayOs trong Press Settings.'
            }

        if not name:
            return {
                'code': '1',
                'desc': 'Không tìm thấy giao dịch.'
            }

        payOS = PayOS(client_id=payos_settings.get('payos_client_id'), api_key=payos_settings.get(
            'payos_api_key'), checksum_key=payos_settings.get('payos_checksum_key'))

        webhookData = payOS.verifyPaymentWebhookData(webhookBody)

        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)
        if balance_transaction.docstatus == 1:
            return {
                'code': '1',
                'desc': 'Không thể thanh toán lại.'
            }

        balance_transaction.docstatus = 1
        balance_transaction.save(ignore_permissions=True)

        return {
            'code': '0',
            'desc': 'Thanh toán thành công.'
        }
    except Exception as ex:
        return {
            'code': '1',
            'desc': str(ex)
        }
