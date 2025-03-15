# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from press.overrides import get_permission_query_conditions_for_doctype
from press.press.doctype.team.team import (
    enqueue_finalize_unpaid_for_team
)


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

        # tinh toan lai tat ca so du va cap nhat lai so tien
        ending_balance = info_last_balance[0]['ending_balance'] if info_last_balance else 0
        promotion_balance_1 = info_last_balance[0]['promotion_balance_1'] if info_last_balance else 0
        promotion_balance_2 = info_last_balance[0]['promotion_balance_2'] if info_last_balance else 0
        last_balance = ending_balance + promotion_balance_1 + promotion_balance_2

        if info_last_balance:
            self.ending_balance = ending_balance + self.amount
            self.promotion_balance_1 = promotion_balance_1 + self.amount_promotion_1
            self.promotion_balance_2 = promotion_balance_2 + self.amount_promotion_2
        else:
            self.ending_balance = self.amount
            self.promotion_balance_1 = self.amount_promotion_1
            self.promotion_balance_2 = self.amount_promotion_2

        if self.type == "Adjustment":
            self.unallocated_amount = self.amount
            self.unallocated_amount_1 = self.amount_promotion_1
            self.unallocated_amount_2 = self.amount_promotion_2
            total_unallocated = self.amount + self.amount_promotion_1 + self.amount_promotion_2
            if total_unallocated < 0:
                # in case of credit transfer
                self.consume_unallocated_amount()
                self.unallocated_amount = 0
                self.unallocated_amount_1 = 0
                self.unallocated_amount_2 = 0
            elif last_balance < 0 and abs(last_balance) <= total_unallocated:
                # previously the balance was negative
                # settle the negative balance
                if ending_balance < 0 and abs(ending_balance) <= self.amount:
                    self.unallocated_amount = self.amount - abs(ending_balance)
                if promotion_balance_1 < 0 and abs(promotion_balance_1) <= self.amount:
                    self.unallocated_amount_1 = self.amount_promotion_1 - \
                        abs(promotion_balance_1)
                if promotion_balance_2 < 0 and abs(promotion_balance_2) <= self.amount:
                    self.unallocated_amount_2 = self.amount_promotion_2 - \
                        abs(promotion_balance_2)

                self.add_comment(
                    text=f"Settling negative balance of {abs(last_balance)}")
            elif last_balance < 0 and abs(last_balance) > total_unallocated:
                frappe.throw(
                    f"Your credit balance is negative. You need to add minimum {abs(last_balance)} prepaid credits."
                )

    def before_update_after_submit(self):
        total_allocated = sum([d.amount for d in self.allocated_to])
        total_allocated_1 = sum(
            [d.amount_promotion_1 for d in self.allocated_to])
        total_allocated_2 = sum(
            [d.amount_promotion_2 for d in self.allocated_to])
        self.unallocated_amount = self.amount - total_allocated
        self.unallocated_amount_1 = self.amount_promotion_1 - total_allocated_1
        self.unallocated_amount_2 = self.amount_promotion_2 - total_allocated_2

    def on_submit(self):
        user_team = frappe.db.get_value("Team", self.team, "user")
        frappe.publish_realtime("balance_updated", user=user_team)

    def consume_unallocated_amount(self):
        self.validate_total_unallocated_amount()

        allocation_map = {}
        remaining_amount = abs(self.amount)
        remaining_amount_1 = abs(self.amount_promotion_1)
        remaining_amount_2 = abs(self.amount_promotion_2)
        
        transactions = frappe.get_all(
			"Balance Transaction",
			filters={"docstatus": 1, "team": self.team},
            or_filters={"unallocated_amount": (">", 0), "unallocated_amount_1": (">", 0), "unallocated_amount_2": (">", 0)},
			fields=["name", "unallocated_amount", "unallocated_amount_1", "unallocated_amount_2"],
			order_by="creation asc",
		)
        
        for transaction in transactions:
            if not allocation_map.get(transaction.name):
                allocation_map[transaction.name] = {
                    'amount': 0,
                    'amount_1': 0,
                    'amount_2': 0,
                }

            if remaining_amount > 0:
                total_unallocated_amount = transaction.unallocated_amount
                allocated_amount = min(
                    remaining_amount, total_unallocated_amount)
                remaining_amount -= allocated_amount
                allocation_map[transaction.name]['amount'] = allocated_amount

            if remaining_amount_1 > 0:
                total_unallocated_amount = transaction.unallocated_amount_1
                allocated_amount = min(
                    remaining_amount_1, total_unallocated_amount)
                remaining_amount_1 -= allocated_amount
                allocation_map[transaction.name]['amount_1'] = allocated_amount

            if remaining_amount_2 > 0:
                total_unallocated_amount = transaction.unallocated_amount_2
                allocated_amount = min(
                    remaining_amount_2, total_unallocated_amount)
                remaining_amount_2 -= allocated_amount
                allocation_map[transaction.name]['amount_2'] = allocated_amount

        for transaction, val in allocation_map.items():
            doc = frappe.get_doc("Balance Transaction", transaction)
            doc.append(
                "allocated_to",
                {
                    "amount": abs(val['amount']),
                    "amount_promotion_1": abs(val['amount_1']),
                    "amount_promotion_2": abs(val['amount_2']),
                    "currency": self.currency,
                    "balance_transaction": self.name,
                },
            )
            doc.save(ignore_permissions=True)

    def validate_total_unallocated_amount(self):
        total_amount = self.amount + self.amount_promotion_1 + self.amount_promotion_2
        unallocated_amount = (
            frappe.get_all(
                "Balance Transaction",
                filters={"docstatus": 1, "team": self.team},
                or_filters={"unallocated_amount": (">", 0), "unallocated_amount_1": (">", 0), "unallocated_amount_2": (">", 0)},
                fields=["sum(unallocated_amount) as total_unallocated_amount", "sum(unallocated_amount_1) as total_unallocated_amount_1", "sum(unallocated_amount_2) as total_unallocated_amount_2"],
            )[0]
            or []
        )
        if not unallocated_amount:
            frappe.throw(
                "Cannot create transaction as no unallocated amount found")

        total_unallocated_amount = unallocated_amount.total_unallocated_amount + \
            unallocated_amount.total_unallocated_amount_1 + \
            unallocated_amount.total_unallocated_amount_2
        if total_unallocated_amount < abs(total_amount):
            frappe.throw(
                f"Cannot create transaction as unallocated amount {total_unallocated_amount} is less than {total_amount}"
            )


get_permission_query_conditions = get_permission_query_conditions_for_doctype(
    "Balance Transaction"
)

@frappe.whitelist()
def handling_upon_recharge(team):
    enqueue_finalize_unpaid_for_team(team)
    return {}

def handle_for_expired_promotions():
    date_now = frappe.utils.now_datetime().date()
    transactions = frappe.get_all(
        "Balance Transaction",
        filters={"docstatus": 1, "unallocated_amount_1": (">", 0)},
        fields=["name", "team", "currency", "date_promotion_1", "unallocated_amount_1", "promotion1_amount_used"],
        order_by="creation asc",
    )

    for tran in transactions:
        if tran.date_promotion_1 and tran.date_promotion_1 <= date_now:
            doc = frappe.get_doc(
                doctype="Balance Transaction",
                team=tran.team,
                type="Promotion",
                source="Free Credits",
                currency=tran.currency,
                amount=0,
                amount_promotion_1=tran.unallocated_amount_1 * -1,
                promotion1_amount_used=tran.promotion1_amount_used * -1,
                amount_promotion_2=0,
                description=f"Hết hạn khuyến mãi 1",
            )
            doc.insert()
            doc.submit()
