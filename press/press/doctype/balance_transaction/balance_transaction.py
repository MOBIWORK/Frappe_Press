# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from press.overrides import get_permission_query_conditions_for_doctype
from press.utils import check_promotion


class BalanceTransaction(Document):
    def validate(self):
        if not self.amount:
            self.amount = 0
        if not self.amount_promotion_1:
            self.amount_promotion_1 = 0
        if not self.amount_promotion_2:
            self.amount_promotion_2 = 0

        total_amount = self.amount + \
            self.amount_promotion_1 + self.amount_promotion_2
        if total_amount == 0:
            frappe.throw("Amount cannot be 0")

    def before_submit(self):
        info_last_balance = frappe.db.get_all(
            "Balance Transaction",
            filters={"team": self.team, "docstatus": 1},
            fields=["sum(amount) as ending_balance", "sum(amount_promotion_1) as promotion_balance_1",
                    "sum(amount_promotion_2) as promotion_balance_2"],
            group_by="team",
        )

        # kiem tra xem ngay dang ky khuyen mai da co chua va cap nhat
        # dang ky khuyen mai cho giao dich hien tai
        if not self.date_promotion_1:
            date_promotion_1 = frappe.db.get_all(
                "Balance Transaction",
                fields=['date_promotion_1'],
                filters={"team": self.team, "docstatus": 1},
                order_by="creation desc",
                pluck='date_promotion_1',
                limit=1,
            )
            date_promotion_1 = date_promotion_1[0] if date_promotion_1 else None
            self.date_promotion_1 = date_promotion_1

        # kiem tra da het han khuyen mai 1 chua
        # neu het han(False) thi reset khuyen mai 1 ve 0
        val_check_promotion = check_promotion(self.team, self.date_promotion_1)
        if not val_check_promotion:
            self.promotion_balance_1 = 0
        # tinh toan lai tat ca so du va cap nhat lai so tien
        if info_last_balance:
            info_last_balance = info_last_balance[0]
            ending_balance = info_last_balance['ending_balance']
            promotion_balance_1 = info_last_balance['promotion_balance_1']
            promotion_balance_2 = info_last_balance['promotion_balance_2']
            if not val_check_promotion:
                self.amount_promotion_1 = promotion_balance_1 * -1
            self.ending_balance = ending_balance + self.amount
            self.promotion_balance_1 = promotion_balance_1 + self.amount_promotion_1
            self.promotion_balance_2 = promotion_balance_2 + self.amount_promotion_2
        else:
            self.ending_balance = self.amount
            self.promotion_balance_1 = self.amount_promotion_1
            self.promotion_balance_2 = self.amount_promotion_2

        last_balance = self.ending_balance + \
            self.promotion_balance_1 + self.promotion_balance_2

        if self.type == "Adjustment":
            self.unallocated_amount = self.amount + \
                self.amount_promotion_1 + self.amount_promotion_2
            if self.unallocated_amount < 0:
                # in case of credit transfer
                self.consume_unallocated_amount()
                self.unallocated_amount = 0
            elif last_balance < 0 and abs(last_balance) <= self.unallocated_amount:
                # previously the balance was negative
                # settle the negative balance
                self.unallocated_amount = self.unallocated_amount - \
                    abs(last_balance)
                self.add_comment(
                    text=f"Settling negative balance of {abs(last_balance)}")
            elif last_balance < 0 and abs(last_balance) > self.unallocated_amount:
                frappe.throw(
                    f"Your credit balance is negative. You need to add minimum {abs(last_balance)} prepaid credits."
                )

    def before_update_after_submit(self):
        total_amount = self.amount + self.amount_promotion_1 + self.amount_promotion_2
        total_allocated = sum([d.amount for d in self.allocated_to]) + sum(
            [d.amount_promotion_1 for d in self.allocated_to]) + sum([d.amount_promotion_2 for d in self.allocated_to])
        self.unallocated_amount = total_amount - total_allocated

    def on_submit(self):
        frappe.publish_realtime("balance_updated", user=self.team)

    def consume_unallocated_amount(self):
        self.validate_total_unallocated_amount()

        allocation_map = {}
        remaining_amount = abs(
            self.amount + self.amount_promotion_1 + self.amount_promotion_2)
        transactions = frappe.get_all(
            "Balance Transaction",
            filters={"docstatus": 1, "team": self.team,
                     "unallocated_amount": (">", 0)},
            fields=["name", "unallocated_amount"],
            order_by="creation asc",
        )
        for transaction in transactions:
            if remaining_amount <= 0:
                break
            allocated_amount = min(
                remaining_amount, transaction.unallocated_amount)
            remaining_amount -= allocated_amount
            allocation_map[transaction.name] = allocated_amount

        for transaction, amount in allocation_map.items():
            doc = frappe.get_doc("Balance Transaction", transaction)
            doc.append(
                "allocated_to",
                {
                    "amount": abs(amount),
                    "currency": self.currency,
                    "balance_transaction": self.name,
                },
            )
            doc.save(ignore_permissions=True)

    def validate_total_unallocated_amount(self):
        total_amount = self.amount + self.amount_promotion_1 + self.amount_promotion_2
        total_unallocated_amount = (
            frappe.get_all(
                "Balance Transaction",
                filters={"docstatus": 1, "team": self.team,
                         "unallocated_amount": (">", 0)},
                fields=["sum(unallocated_amount) as total_unallocated_amount"],
                pluck="total_unallocated_amount",
            )
            or []
        )
        if not total_unallocated_amount:
            frappe.throw(
                "Cannot create transaction as no unallocated amount found")
        if total_unallocated_amount[0] < abs(total_amount):
            frappe.throw(
                f"Cannot create transaction as unallocated amount {total_unallocated_amount[0]} is less than {total_amount}"
            )


get_permission_query_conditions = get_permission_query_conditions_for_doctype(
    "Balance Transaction"
)


def except_for_expired_promotions():
    from datetime import timedelta

    number_days_promotion = frappe.db.get_single_value(
        "Press Settings", "number_days_promotion") or 0
    date_expire = frappe.utils.now_datetime()
    date_expire = date_expire - timedelta(days=number_days_promotion)
    date_expire = date_expire.strftime('%Y-%m-%d')

    transactions = frappe.db.sql(
        f"""
			SELECT b.team, b.currency, b.promotion_balance_1, MAX(b.creation) as creation
			FROM `tabBalance Transaction` b
			WHERE b.date_promotion_1 <= '{date_expire}' AND b.promotion_balance_1 > 0
            AND b.docstatus = 1
			GROUP BY b.team
		""",
        as_dict=True,
    )

    for tran in transactions:
        doc = frappe.get_doc(
            doctype="Balance Transaction",
            team=tran.get('team'),
            type="Poromotion",
            source="Free Credits",
            currency=tran.get('currency'),
            amount=0,
            amount_promotion_1=tran.get('promotion_balance_1') * -1,
            amount_promotion_2=0,
            description=f"Hết hạn khuyến mãi 1",
        )
        doc.insert()
        doc.submit()
