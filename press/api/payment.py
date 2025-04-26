# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import fmt_money

from press.utils import check_payos_settings
from payos import PayOS
from jinja2 import Template
from press.api.language import get_language_from_team


@frappe.whitelist()
def all():
    payments = frappe.get_all(
        "Payment", fields=["name"], filters={"user": frappe.session.user}
    )
    return payments


def send_email_confirm_money_into_account(balance_transaction):
    try:
        msg = ''

        if not balance_transaction:
            return "Không tìm thấy giao dịch"

        team_name = balance_transaction.team
        if not team_name:
            return 'Không tìm thấy người dùng'

        lang = get_language_from_team(team_name)
        lang = lang if lang in ['vi', 'en'] else 'vi'

        team = frappe.get_doc("Team", team_name)

        billing_details = None
        if team and team.billing_address:
            billing_details = frappe.get_doc(
                "Address", team.billing_address)

        if billing_details:
            # Thay thế giá trị của biến trong mẫu
            transaction_type = _('Deposit into account', lang)
            trading_code = balance_transaction.order_code
            formattor_amount = fmt_money(
                balance_transaction.amount, 0)
            amount = f'+{formattor_amount} VND'
            formattor_balance = fmt_money(
                balance_transaction.ending_balance, 0)
            balance = f'{formattor_balance} VND'
            transaction_time = balance_transaction.modified.strftime(
                '%H:%M:%S')
            transaction_date = balance_transaction.modified.strftime(
                '%d/%m/%Y')
            transaction_information = 'Nap tien TK MBWCloud tu PayOs'

            pre_subject = "[MBWCloud] - "
            subject = pre_subject + _("Top-up successful", lang)
            
            # get language template
            template = "confirm_money_into_account"
            template = f"{lang}_{template}"
            
            email_recipients = team.get_email_invoice()
            frappe.sendmail(
                recipients=email_recipients,
                subject=subject,
                template=template,
                args={
                    "customer_name": billing_details.address_title,
                    "transaction_type": transaction_type,
                    "trading_code": trading_code,
                    "amount": amount,
                    "balance": balance,
                    "transaction_time": transaction_time,
                    "transaction_date": transaction_date,
                    "transaction_information": transaction_information
                }
            )
        else:
            msg = 'Không có địa chỉ gửi email'

        return msg
    except Exception as ex:
        return str(ex)


@frappe.whitelist(allow_guest=True, methods=['POST'])
def webhook_payment(**webhookBody):
    doc_log = frappe.new_doc("PayOs Webhook Log")
    doc_log.webhook_body = frappe.as_json(webhookBody)
    doc_log.code = '1'
    doc_log.flags.ignore_mandatory = True

    try:
        payos_settings = check_payos_settings()
        data = webhookBody.get('data')
        if type(data) != dict:
            msg = 'Dữ liệu webhook không đúng định dạng.'
            doc_log.message = msg
            doc_log.insert(ignore_permissions=True)
            return {
                'code': '1',
                'desc': msg
            }

        name = frappe.db.get_value(
            'Balance Transaction', {'order_code': data.get('orderCode')}, ['name'])
        if not payos_settings:
            msg = 'Vui lòng cấu hình đầy đủ thông tin PayOs trong Press Settings.'
            doc_log.message = msg
            doc_log.insert(ignore_permissions=True)

            return {
                'code': '1',
                'desc': msg
            }

        if not name:
            msg = 'Không tìm thấy giao dịch.'
            doc_log.message = msg
            doc_log.insert(ignore_permissions=True)

            return {
                'code': '1',
                'desc': msg
            }

        payOS = PayOS(client_id=payos_settings.get('payos_client_id'), api_key=payos_settings.get(
            'payos_api_key'), checksum_key=payos_settings.get('payos_checksum_key'))

        webhookData = payOS.verifyPaymentWebhookData(webhookBody)

        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)
        if balance_transaction.docstatus != 0:
            msg = 'Giao dịch đã thanh toán hoặc hủy trước đó.'
            doc_log.message = msg
            doc_log.insert(ignore_permissions=True)
            return {
                'code': '1',
                'desc': msg
            }

        balance_transaction.docstatus = 1
        balance_transaction.payos_payment_status = "PAID"
        balance_transaction.save(ignore_permissions=True)

        # send email template
        msg = 'Thanh toán thành công.'
        balance_transaction.reload()
        msg_send = msg + ' | ' + send_email_confirm_money_into_account(
            balance_transaction) 

        doc_log.code = '00'
        doc_log.message = msg_send
        doc_log.invoice_id = data.get('reference')
        doc_log.team = balance_transaction.team
        doc_log.balance_transaction = balance_transaction.name
        doc_log.insert(ignore_permissions=True)

        return {
            'code': '00',
            'desc': msg
        }
    except Exception as ex:
        doc_log.code = '1'
        doc_log.message = str(ex)
        doc_log.insert(ignore_permissions=True)

        return {
            'code': '1',
            'desc': str(ex)
        }
