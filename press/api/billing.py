# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe

from typing import Dict, List
from itertools import groupby
from frappe.utils import fmt_money
from frappe.core.utils import find
from press.press.doctype.team.team import has_unsettled_invoices
from press.utils import get_current_team, check_payos_settings
from press.utils.billing import (
    clear_setup_intent,
    get_publishable_key,
    get_setup_intent,
    get_razorpay_client,
    get_stripe,
    make_formatted_doc,
    states_with_tin,
    validate_gstin_check_digit,
    GSTIN_FORMAT,
)

from payos import PayOS, PaymentData

import random
NUMBERCHOICE_HEAD = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
NUMBERCHOICE_BODY = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


@frappe.whitelist()
def get_publishable_key_and_setup_intent():
    team = get_current_team()
    return {
        "publishable_key": get_publishable_key(),
        "setup_intent": get_setup_intent(team),
    }


@frappe.whitelist()
def get_cash_gift_policy():
    cash_policy = frappe.get_list(
        "Cash Gift Policy",
        fields=["*"],
        order_by="amount_from asc",
        ignore_permissions=True
    )
    print(cash_policy)

    return cash_policy


@frappe.whitelist()
def upcoming_invoice():
    team = get_current_team(True)
    invoice = team.get_upcoming_invoice()
    amount_available_credits = team.get_balance()
    amount_upcoming_invoice = 0
    total_unpaid_amount = (
        frappe.get_all(
            "Invoice",
            {"status": "Unpaid", "team": get_current_team(),
             "type": "Subscription"},
            ["sum(total) as total"],
            pluck="total",
        )[0]
        or 0
    )

    if invoice:
        upcoming_invoice = invoice.as_dict()
        upcoming_invoice.formatted = make_formatted_doc(invoice, ["Currency"])
        amount_upcoming_invoice = upcoming_invoice.get('total')
    else:
        upcoming_invoice = None

    available_balances = amount_available_credits - \
        amount_upcoming_invoice - total_unpaid_amount
    return {
        "upcoming_invoice": upcoming_invoice,
        "available_credits": amount_available_credits,
        "amount_available_credits": amount_available_credits,
        "amount_upcoming_invoice": amount_upcoming_invoice,
        "available_balances": available_balances,
        "total_unpaid_amount": total_unpaid_amount
    }


@frappe.whitelist()
def past_invoices():
    return get_current_team(True).get_past_invoices()


@frappe.whitelist()
def invoices_and_payments():
    team = get_current_team(True)
    invoices = team.get_past_invoices()
    return invoices


@frappe.whitelist()
def refresh_invoice_link(invoice):
    doc = frappe.get_doc("Invoice", invoice)
    return doc.refresh_stripe_payment_link()


@frappe.whitelist()
def balances():
    team = get_current_team()

    bt = frappe.qb.DocType("Balance Transaction")
    inv = frappe.qb.DocType("Invoice")

    # delete payment is spam
    query = (
        frappe.qb.from_(bt)
        .where((bt.team == team) & (bt.docstatus == 0) & (bt.checkout_url.isnull() | bt.checkout_url == '') & ((bt.order_code.notnull()) | (bt.order_code != '')))
        .delete()
    )
    query.run(as_dict=True)

    has_bought_credits = frappe.db.get_all(
        "Balance Transaction",
        filters={
            "source": ("in", ("Prepaid Credits", "Transferred Credits", "Free Credits")),
            "team": team,
            # "docstatus": 1,
        },
        limit=1,
    )
    if not has_bought_credits:
        return []

    query = (
        frappe.qb.from_(bt)
        .left_join(inv)
        .on(bt.invoice == inv.name)
        .select(
            bt.name,
            bt.docstatus,
            bt.creation,
            bt.amount,
            bt.currency,
            bt.source,
            bt.type,
            bt.ending_balance,
            bt.checkout_url,
            bt.payos_payment_status,
            inv.period_start,
        )
        .where((bt.team == team))
        .orderby(bt.creation, order=frappe.qb.desc)
    )

    data = query.run(as_dict=True)
    for d in data:
        d.formatted = dict(
            amount=fmt_money(d.amount, 0, d.currency),
        )
        pre_balance = ''
        ending_balance = ''

        if d.ending_balance and d.docstatus == 1:
            pre_balance = fmt_money(d.ending_balance - d.amount, 0, d.currency)
            ending_balance = fmt_money(d.ending_balance, 0, d.currency)
        elif d.ending_balance and d.docstatus == 2:
            pre_balance = fmt_money(d.ending_balance - d.amount, 0, d.currency)
            ending_balance = fmt_money(
                d.ending_balance - d.amount, 0, d.currency)

        d.formatted['pre_balance'] = pre_balance
        d.formatted['ending_balance'] = ending_balance

        if d.period_start:
            d.formatted["invoice_for"] = d.period_start.strftime("%B %Y")
    return data


def get_processed_balance_transactions(transactions: List[Dict]):
    """Cleans up transactions and adjusts ending balances accordingly"""

    cleaned_up_transations = get_cleaned_up_transactions(transactions)
    processed_balance_transactions = []
    for bt in reversed(cleaned_up_transations):
        if is_added_credits_bt(bt) and len(processed_balance_transactions) < 1:
            processed_balance_transactions.append(bt)
        elif is_added_credits_bt(bt):
            bt.ending_balance += processed_balance_transactions[
                -1
            ].ending_balance  # Adjust the ending balance
            processed_balance_transactions.append(bt)
        elif bt.type == "Applied To Invoice":
            processed_balance_transactions.append(bt)

    return list(reversed(processed_balance_transactions))


def get_cleaned_up_transactions(transactions: List[Dict]):
    """Only picks Balance transactions that the users care about"""

    cleaned_up_transations = []
    for bt in transactions:
        if is_added_credits_bt(bt):
            cleaned_up_transations.append(bt)
            continue

        if bt.type == "Applied To Invoice" and not find(
                cleaned_up_transations, lambda x: x.invoice == bt.invoice
        ):
            cleaned_up_transations.append(bt)
            continue
    return cleaned_up_transations


def is_added_credits_bt(bt):
    """Returns `true` if credits were added and not some reverse transaction"""
    if not (
            bt.type == "Adjustment"
            and bt.source
            in (
                "Prepaid Credits",
                "Free Credits",
                "Transferred Credits",
            )  # Might need to re-think this
    ):
        return False

    # Is not a reverse of a previous balance transaction
    bt.description = bt.description or ""
    return not bt.description.startswith("Reverse")


@frappe.whitelist()
def details():
    team = get_current_team(True)
    address = None
    if team.billing_address:
        address = frappe.get_doc("Address", team.billing_address)
        country = "Việt Nam" if address.country == "Vietnam" else address.country
        address_parts = [
            address.address_line1,
            address.county,
            address.state,
            country,
            address.pincode,
        ]
        billing_address = ", ".join([d for d in address_parts if d])
    else:
        billing_address = ""

    return {
        "address": address,
        "billing_name": team.billing_name,
        "billing_address": billing_address,
        "gstin": address.gstin if address else None,
    }


@frappe.whitelist()
def get_customer_details(team):
    """This method is called by frappe.io for creating Customer and Address"""
    team_doc = frappe.db.get_value("Team", team, "*")
    return {
        "team": team_doc,
        "address": frappe.get_doc("Address", team_doc.billing_address),
    }


@frappe.whitelist()
def create_payment_intent_for_micro_debit(payment_method_name):
    team = get_current_team(True)
    stripe = get_stripe()
    amount = 50 if team.currency == "USD" else 5000

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=team.currency.lower(),
        customer=team.stripe_customer_id,
        description="Micro-Debit Card Test Charge",
        metadata={
            "payment_for": "micro_debit_test_charge",
                    "payment_method_name": payment_method_name,
        },
    )
    return {"client_secret": intent["client_secret"]}


def generator_order_code(number=12):
    order_code = ''
    for i in range(number-1):
        str_choice = random.choice(NUMBERCHOICE_BODY)
        order_code += str_choice
    order_code = random.choice(NUMBERCHOICE_HEAD) + order_code

    return order_code


@frappe.whitelist()
def create_order(amount):
    try:
        team = get_current_team()
        amount = round(amount)
        remark = "Nap tien TK MBW Cloud"

        payos_settings = check_payos_settings()
        if not payos_settings:
            return {
                'code': '1',
                'desc': 'Chưa thể nạp tiền ngay lúc này, vui lòng thử lại sau.'
            }

        # check exists pre payment
        check_pre_payment = frappe.db.exists(
            "Balance Transaction",
            {
                "team": team,
                "payos_payment_status": "PENDING"
            }
        )

        if check_pre_payment:
            return {
                'code': '1',
                'desc': 'Vui lòng thanh toán giao dịch nạp tiền trước đó.'
            }

        # check orderCode exsists
        order_code = generator_order_code()
        checkOrder = frappe.db.exists('Balance Transaction', {
            'order_code': order_code
        })
        while checkOrder:
            order_code = generator_order_code()
            checkOrder = frappe.db.exists('Balance Transaction', {
                'order_code': order_code
            })

        doc = frappe.get_doc(
            order_code=order_code,
            doctype="Balance Transaction",
            team=team,
            type="Adjustment",
            source='Prepaid Credits',
            amount=amount,
            description=remark,
            payos_payment_status='PROCESSING'
        )
        doc.insert(ignore_permissions=True)

        infoOrder = doc.as_dict()
        return {
            'code': '00',
            'infoOrder': infoOrder,
            'desc': 'Success'
        }
    except Exception as ex:
        return {
            'code': '1',
            'desc': str(ex)
        }


@frappe.whitelist()
def payos_return_cancel_order(order_code):
    try:
        name = frappe.db.get_value(
            'Balance Transaction', {'order_code': order_code}, ['name'])

        if not name:
            return {
                'code': '1',
                'desc': 'Không tìm thấy giao dịch.'
            }

        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)
        if balance_transaction.docstatus != 0 or balance_transaction.payos_payment_status == "CANCELLED":
            return {
                'code': '1',
                'desc': "Giao dịch đã được hủy trước đó"
            }

        balance_transaction.payos_payment_status = 'CANCELLED'
        balance_transaction.docstatus = 1
        balance_transaction.save(ignore_permissions=True)

        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)
        balance_transaction.docstatus = 2
        balance_transaction.save(ignore_permissions=True)

        return {
            'code': '00',
            'desc': 'Success'
        }
    except Exception as ex:
        return {
            'code': '1',
            'desc': str(ex)
        }


@frappe.whitelist()
def cancel_order(name):
    try:
        payos_settings = check_payos_settings()
        balance_transaction = frappe.get_doc(
            "Balance Transaction", name)

        if not payos_settings or not balance_transaction:
            return {
                'code': '1',
                'desc': 'Chưa thể hủy giao dịch ngay lúc này, vui lòng thử lại sau.'
            }

        payOS = PayOS(client_id=payos_settings.get('payos_client_id'), api_key=payos_settings.get(
            'payos_api_key'), checksum_key=payos_settings.get('payos_checksum_key'))

        paymentLinkInfo = payOS.cancelPaymentLink(
            orderId=balance_transaction.get('order_code'))
        if paymentLinkInfo.status == "CANCELLED":
            balance_transaction.payos_payment_status = 'CANCELLED'
            balance_transaction.docstatus = 1
            balance_transaction.save(ignore_permissions=True)

            balance_transaction = frappe.get_doc(
                "Balance Transaction", name)
            balance_transaction.docstatus = 2
            balance_transaction.save(ignore_permissions=True)

            return {
                'code': '00',
                'desc': 'Success'
            }
        else:
            return {
                'code': '1',
                'desc': 'Hủy thất bại.'
            }
    except Exception as ex:
        return {
            'code': '1',
            'desc': str(ex)
        }


@frappe.whitelist()
def get_link_payment_payos(info_order):
    try:
        payos_settings = check_payos_settings()
        balance_transaction = frappe.get_doc(
            "Balance Transaction", info_order.get('name'))

        if not payos_settings or not balance_transaction:
            return {
                'code': '1',
                'desc': 'Chưa thể nạp tiền ngay lúc này, vui lòng thử lại sau.'
            }

        payOS = PayOS(client_id=payos_settings.get('payos_client_id'), api_key=payos_settings.get(
            'payos_api_key'), checksum_key=payos_settings.get('payos_checksum_key'))

        paymentData = PaymentData(
            orderCode=int(info_order.get('order_code')),
            amount=info_order.get('amount'),
            description=info_order.get('description'),
            cancelUrl=payos_settings.get('payos_cancel_url'),
            returnUrl=payos_settings.get('payos_return_url')
        )

        paymentLinkData = payOS.createPaymentLink(paymentData=paymentData)
        balance_transaction.checkout_url = paymentLinkData.checkoutUrl
        balance_transaction.payos_payment_status = 'PENDING'
        balance_transaction.save(ignore_permissions=True)

        return {
            'code': '00',
            'infoPayment': {
                "checkoutUrl": paymentLinkData.checkoutUrl,
                "orderCode": paymentLinkData.orderCode,
                "amount": paymentLinkData.amount
            },
            'desc': 'Success'
        }
    except Exception as ex:
        return {
            'code': '1',
            'desc': str(ex)
        }


@frappe.whitelist()
def create_payment_intent_for_buying_credits(amount):
    team = get_current_team(True)
    metadata = {"payment_for": "prepaid_credits"}

    if team.currency == "INR":
        gst_amount = amount * \
            frappe.db.get_single_value("Press Settings", "gst_percentage")
        amount += gst_amount
        metadata.update({"gst": round(gst_amount, 2)})

    amount = round(amount, 2)
    stripe = get_stripe()
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency=team.currency.lower(),
        customer=team.stripe_customer_id,
        description="Prepaid Credits",
        metadata=metadata,
    )
    return {
        "client_secret": intent["client_secret"],
        "publishable_key": get_publishable_key(),
    }


@frappe.whitelist()
def create_payment_intent_for_prepaid_app(amount, metadata):
    stripe = get_stripe()
    team = get_current_team(True)
    payment_method = frappe.get_value(
        "Stripe Payment Method", team.default_payment_method, "stripe_payment_method_id"
    )
    try:
        if not payment_method:
            intent = stripe.PaymentIntent.create(
                amount=amount * 100,
                currency=team.currency.lower(),
                customer=team.stripe_customer_id,
                description="Prepaid App Purchase",
                metadata=metadata,
            )
        else:
            intent = stripe.PaymentIntent.create(
                amount=amount * 100,
                currency=team.currency.lower(),
                customer=team.stripe_customer_id,
                description="Prepaid App Purchase",
                off_session=True,
                confirm=True,
                metadata=metadata,
                payment_method=payment_method,
                payment_method_options={
                    "card": {"request_three_d_secure": "any"}},
            )

        return {
            "payment_method": payment_method,
            "client_secret": intent["client_secret"],
            "publishable_key": get_publishable_key(),
        }
    except stripe.error.CardError as e:
        err = e.error
        if err.code == "authentication_required":
            # Bring the customer back on-session to authenticate the purchase
            return {
                "error": "authentication_required",
                "payment_method": err.payment_method.id,
                "amount": amount,
                "card": err.payment_method.card,
                "publishable_key": get_publishable_key(),
                "client_secret": err.payment_intent.client_secret,
            }
        elif err.code:
            # The card was declined for other reasons (e.g. insufficient funds)
            # Bring the customer back on-session to ask them for a new payment method
            return {
                "error": err.code,
                "payment_method": err.payment_method.id,
                "publishable_key": get_publishable_key(),
                "client_secret": err.payment_intent.client_secret,
            }


@frappe.whitelist()
def get_payment_methods():
    team = get_current_team()
    return frappe.get_doc("Team", team).get_payment_methods()


@frappe.whitelist()
def set_as_default(name):
    payment_method = frappe.get_doc(
        "Stripe Payment Method", {"name": name, "team": get_current_team()}
    )
    payment_method.set_default()


@frappe.whitelist()
def remove_payment_method(name):
    team = get_current_team()
    payment_method_count = frappe.db.count(
        "Stripe Payment Method", {"team": team})

    if has_unsettled_invoices(team) and payment_method_count == 1:
        return "Unpaid Invoices"

    payment_method = frappe.get_doc("Stripe Payment Method", {
                                    "name": name, "team": team})
    payment_method.delete()


@frappe.whitelist()
def finalize_invoices():
    unsettled_invoices = frappe.get_all(
        "Invoice",
        {"team": get_current_team(), "status": ("in", ("Draft", "Unpaid"))},
        pluck="name",
    )

    for inv in unsettled_invoices:
        inv_doc = frappe.get_doc("Invoice", inv)
        inv_doc.finalize_invoice()


@frappe.whitelist()
def unpaid_invoices():
    team = get_current_team()
    invoices = frappe.get_all(
        "Invoice",
        {"team": team, "status": (
            "in", ["Draft", "Unpaid"]), "type": "Subscription"},
        ["name", "status", "period_end", "currency", "amount_due", "total"],
        order_by="creation asc",
    )

    return invoices


@frappe.whitelist()
def change_payment_mode(mode):
    team = get_current_team(get_doc=True)
    team.payment_mode = mode
    if team.partner_email and mode == "Paid By Partner" and not team.billing_team:
        team.billing_team = frappe.db.get_value(
            "Team",
            {"enabled": 1, "erpnext_partner": 1,
             "partner_email": team.partner_email},
            "name",
        )
    if team.billing_team and mode != "Paid By Partner":
        team.billing_team = ""
    team.save()


@frappe.whitelist()
def prepaid_credits_via_onboarding():
    """When prepaid credits are bought, the balance is not immediately reflected.
    This method will check balance every second and then set payment_mode"""
    from time import sleep

    team = get_current_team(get_doc=True)

    seconds = 0
    # block until balance is updated
    while team.get_balance() == 0 or seconds > 20:
        seconds += 1
        sleep(1)
        frappe.db.rollback()

    team.payment_mode = "Prepaid Credits"
    team.save()


@frappe.whitelist()
def get_invoice_usage(invoice):
    team = get_current_team()
    # apply team filter for safety
    doc = frappe.get_doc("Invoice", {"name": invoice, "team": team})
    out = doc.as_dict()
    # a dict with formatted currency values for display
    out.formatted = make_formatted_doc(doc)
    out.invoice_pdf = doc.invoice_pdf or (
        doc.currency == "VND" and doc.get_pdf())
    return out


@frappe.whitelist()
def get_summary():
    team = get_current_team()
    invoices = frappe.get_all(
        "Invoice",
        filters={"team": team, "status": ("in", ["Paid", "Unpaid"])},
        fields=[
            "name",
            "status",
            "period_end",
            "payment_mode",
            "type",
            "currency",
            "amount_paid",
        ],
        order_by="creation desc",
    )

    invoice_names = [x.name for x in invoices]
    grouped_invoice_items = get_grouped_invoice_items(invoice_names)

    for invoice in invoices:
        invoice.items = grouped_invoice_items.get(invoice.name, [])

    return invoices


def get_grouped_invoice_items(invoices: List[str]) -> Dict:
    """Takes a list of invoices (invoice names) and returns a dict of the form:
    { "<invoice_name1>": [<invoice_items>], "<invoice_name2>": [<invoice_items>], }
    """
    invoice_items = frappe.get_all(
        "Invoice Item",
        filters={"parent": ("in", invoices)},
        fields=[
            "amount",
            "document_name AS name",
            "document_type AS type",
            "parent",
            "quantity",
            "rate",
            "plan",
        ],
    )

    grouped_items = groupby(invoice_items, key=lambda x: x["parent"])
    invoice_items_map = {}
    for invoice_name, items in grouped_items:
        invoice_items_map[invoice_name] = list(items)

    return invoice_items_map


@frappe.whitelist()
def after_card_add():
    clear_setup_intent()


@frappe.whitelist()
def setup_intent_success(setup_intent, address=None):
    # setup_intent = frappe._dict(setup_intent)
    # team = get_current_team(True)
    # clear_setup_intent()
    # payment_method = team.create_payment_method(
    #     setup_intent.payment_method, set_default=True
    # )

    team = get_current_team(True)
    clear_setup_intent()
    payment_method = team.create_payment_method(
        '', set_default=True
    )
    if address:
        address = frappe._dict(address)
        team.update_billing_details(address)

    return {"payment_method_name": 'Prepaid Credits'}


@frappe.whitelist()
def validate_gst(address, method=None):
    if isinstance(address, dict):
        address = frappe._dict(address)

    if address.country != "India":
        return

    if address.state not in states_with_tin:
        frappe.throw("Invalid State for India.")

    if not address.gstin:
        frappe.throw("GSTIN is required for Indian customers.")

    if address.gstin and address.gstin != "Not Applicable":
        if not GSTIN_FORMAT.match(address.gstin):
            frappe.throw(
                "Invalid GSTIN. The input you've entered does not match the format of GSTIN."
            )

        tin_code = states_with_tin[address.state]
        if not address.gstin.startswith(tin_code):
            frappe.throw(
                f"GSTIN must start with {tin_code} for {address.state}.")

        validate_gstin_check_digit(address.gstin)


@frappe.whitelist()
def get_latest_unpaid_invoice():
    team = get_current_team()
    unpaid_invoices = frappe.get_all(
        "Invoice",
        {"team": team, "status": "Unpaid",
         "payment_attempt_count": (">", 0)},
        pluck="name",
        order_by="creation desc",
        limit=1,
    )

    if unpaid_invoices:
        unpaid_invoice = frappe.db.get_value(
            "Invoice",
            unpaid_invoices[0],
            ["amount_due", "payment_mode", "amount_due", "currency"],
            as_dict=True,
        )
        if (
                unpaid_invoice.payment_mode == "Prepaid Credits"
                and team_has_balance_for_invoice(unpaid_invoice)
        ):
            return

        return unpaid_invoice


def team_has_balance_for_invoice(prepaid_mode_invoice):
    team = get_current_team(get_doc=True)
    return team.get_balance() >= prepaid_mode_invoice.amount_due


@frappe.whitelist()
def get_partner_credits():
    team = get_current_team(get_doc=True)
    available_credits = team.get_available_partner_credits()
    # return fmt_money(available_credits, 2, team.currency)
    return available_credits


@frappe.whitelist()
def create_razorpay_order(amount):
    client = get_razorpay_client()
    team = get_current_team(get_doc=True)

    if team.currency == "INR":
        gst_amount = amount * \
            frappe.db.get_single_value("Press Settings", "gst_percentage")
        amount += gst_amount

    amount = round(amount, 2)
    data = {
        "amount": int(amount * 100),
        "currency": team.currency,
        "notes": {
            "Description": "Order for MBW Cloud Prepaid Credits",
            "Team (MBW Cloud ID)": team.name,
            "gst": gst_amount if team.currency == "INR" else 0,
        },
    }
    order = client.order.create(data=data)

    payment_record = frappe.get_doc(
        {"doctype": "Razorpay Payment Record",
            "order_id": order.get("id"), "team": team.name}
    ).insert(ignore_permissions=True)

    return {
        "order_id": order.get("id"),
        "key_id": client.auth[0],
        "payment_record": payment_record.name,
    }


@frappe.whitelist()
def handle_razorpay_payment_success(response):
    client = get_razorpay_client()
    client.utility.verify_payment_signature(response)

    payment_record = frappe.get_doc(
        "Razorpay Payment Record",
        {"order_id": response.get("razorpay_order_id")},
        for_update=True,
    )
    payment_record.update(
        {
            "payment_id": response.get("razorpay_payment_id"),
            "signature": response.get("razorpay_signature"),
            "status": "Captured",
        }
    )
    payment_record.save(ignore_permissions=True)


@frappe.whitelist()
def handle_razorpay_payment_failed(response):
    payment_record = frappe.get_doc(
        "Razorpay Payment Record",
        {"order_id": response["error"]["metadata"].get("order_id")},
        for_update=True,
    )

    payment_record.status = "Failed"
    payment_record.failure_reason = response["error"]["description"]
    payment_record.save(ignore_permissions=True)


@frappe.whitelist()
def total_unpaid_amount():
    return (
        frappe.get_all(
            "Invoice",
            {"status": "Unpaid", "team": get_current_team(),
             "type": "Subscription"},
            ["sum(total) as total"],
            pluck="total",
        )[0]
        or 0
    )


@frappe.whitelist()
def get_all_category():
    return frappe.get_all(
        "Marketplace App Category",
        filters={
            'concerns_feature': 1
        },
    )
