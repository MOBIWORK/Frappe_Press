# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


from typing import List
from press.press.doctype.plan.plan import Plan

import frappe
from frappe.model.document import Document
from press.utils import log_error
from press.overrides import get_permission_query_conditions_for_doctype
from jinja2 import Template


class Subscription(Document):
    def validate(self):
        self.validate_duplicate()

    def on_update(self):
        doc = self.get_subscribed_document()
        plan_field = doc.meta.get_field("plan")
        if not (plan_field and plan_field.options == "Plan"):
            return

        if self.enabled and doc.plan != self.plan:
            doc.plan = self.plan
            doc.save()
        if not self.enabled and doc.plan:
            doc.plan = ""
            doc.save()

    def enable(self):
        try:
            self.enabled = True
            self.save()
        except Exception:
            frappe.log_error(title="Enable Subscription Error")

    def disable(self):
        try:
            self.enabled = False
            self.save()
        except Exception:
            frappe.log_error(title="Disable Subscription Error")

    @frappe.whitelist()
    def create_usage_record(self):
        cannot_charge = not self.can_charge_for_subscription()
        if cannot_charge:
            return

        if self.is_usage_record_created():
            return

        team = frappe.get_cached_doc("Team", self.team)

        if team.parent_team:
            team = frappe.get_cached_doc("Team", team.parent_team)

        if team.billing_team and team.payment_mode == "Paid By Partner":
            team = frappe.get_cached_doc("Team", team.billing_team)

        if not team.get_upcoming_invoice():
            team.create_upcoming_invoice()

        plan = frappe.get_cached_doc("Plan", self.plan)
        amount = plan.get_price_for_interval(self.interval, team.currency)

        usage_record = frappe.get_doc(
            doctype="Usage Record",
            team=team.name,
            document_type=self.document_type,
            document_name=self.document_name,
            plan=plan.name,
            amount=amount,
            subscription=self.name,
            interval=self.interval,
            site=frappe.get_value(
                "Marketplace App Subscription", self.marketplace_app_subscription, "site"
            )
            if self.document_type == "Marketplace App"
            else None,
        )
        usage_record.insert()
        usage_record.submit()
        return usage_record

    def can_charge_for_subscription(self):
        doc = self.get_subscribed_document()
        if not doc:
            return False

        if hasattr(doc, "can_charge_for_subscription"):
            return doc.can_charge_for_subscription(self)

        return True

    def is_usage_record_created(self):
        filters = {
            "team": self.team,
            "document_type": self.document_type,
            "document_name": self.document_name,
            "subscription": self.name,
            "interval": self.interval,
            "plan": self.plan,
        }

        if self.interval == "Daily":
            filters.update({"date": frappe.utils.today()})

        if self.interval == "Monthly":
            date = frappe.utils.getdate()
            first_day = frappe.utils.get_first_day(date)
            last_day = frappe.utils.get_last_day(date)
            filters.update({"date": ("between", (first_day, last_day))})

        result = frappe.db.get_all("Usage Record", filters=filters, limit=1)
        return bool(result)

    def validate_duplicate(self):
        if not self.is_new():
            return
        filters = {
            "team": self.team,
            "document_type": self.document_type,
            "document_name": self.document_name,
        }
        if self.document_type == "Marketplace App":
            filters.update(
                {"marketplace_app_subscription": self.marketplace_app_subscription})

        results = frappe.db.get_all(
            "Subscription",
            filters,
            pluck="name",
            limit=1,
        )
        if results:
            link = frappe.utils.get_link_to_form("Subscription", results[0])
            frappe.throw(
                f"A Subscription already exists: {link}", frappe.DuplicateEntryError)

    def get_subscribed_document(self):
        if not hasattr(self, "_subscribed_document"):
            self._subscribed_document = frappe.get_doc(
                self.document_type, self.document_name)
        return self._subscribed_document

    @classmethod
    def get_sites_without_offsite_backups(cls) -> List[str]:
        plans = Plan.get_ones_without_offsite_backups()
        return frappe.get_all(
            "Subscription",
            filters={"document_type": "Site", "plan": ("in", plans)},
            pluck="document_name",
        )


def send_email_handle_site(type_email, site_name, team):
    try:
        args = {'site_name': site_name}
        if type_email == 'lock':
            subject = f"""[EOVCloud] - Khóa truy cập vào tổ chức { site_name } của bạn"""
            template = 'site_lock_email'
        elif type_email == 'warning':
            subject = f"""[EOVCloud] - Sắp khóa truy cập vào tổ chức { site_name } của bạn"""
            template = 'site_lock_warning_email'
        elif type_email == 'prior':
            args['number_day'] = (frappe.db.get_single_value(
                "Press Settings", "site_num_days_advance_warning") or 0)
            subject = f"""[EOVCloud] - Số dư tài khoản của bạn không đủ để duy trì tổ chức { site_name }"""
            template = 'insufficient_funds_warning_prior_date'

        if type_email in ['lock', 'warning', 'prior']:
            frappe.sendmail(
                recipients=team.user,
                subject=subject,
                template=template,
                args=args,
                # now=True,
            )
    except Exception as ex:
        log_error(title="Send email handle site", name=str(ex))


def suspend_site_when_account_balance_is_insufficient():
    # from press.press.doctype.subscription.subscription import sites_with_free_hosting, paid_plans, created_usage_records
    try:
        free_sites = sites_with_free_hosting()
        subscriptions = frappe.db.get_all(
            "Subscription",
            fields=['name', 'plan', 'document_name', 'interval', 'team'],
            filters={
                "enabled": True,
                "document_type": "Site",
                "plan": ("in", paid_plans()),
                "name": ("not in", created_usage_records(free_sites)),
                "document_name": ("not in", free_sites),
            },
            limit=2000,
        )

        # khoi tao su du kha dung
        available_balances_team = {}
        balance_prior = {}
        # lay x ngay de tinh toan canh bao
        x_day = (frappe.db.get_single_value(
            "Press Settings", "site_num_days_advance_warning") or 0) + 1
        # so lan canh bao
        num_advance_warning = frappe.db.get_single_value(
            "Press Settings", "num_advance_warning") or 0
        # lay so ngay su dung toi da truoc khi khoa site
        site_num_days_past_lock = frappe.db.get_single_value(
            "Press Settings", "site_num_days_past_lock") or 0
        for sub in subscriptions:
            total_amount = 0
            plan_site = frappe.get_doc("Plan", sub.get('plan'))
            team_name = sub.get('team')
            team = frappe.get_doc("Team", team_name)
            upcoming_invoice = team.get_upcoming_invoice()
            vat = upcoming_invoice.vat if upcoming_invoice else 0
            subscription = frappe.get_doc("Subscription", sub.get('name'))

            if plan_site and team:
                total_amount += plan_site.get_price_for_interval(
                    sub.get('interval'), team.currency)

            site_name = sub.get('document_name')
            apps_sub = frappe.get_all(
                "Marketplace App Subscription",
                fields=['name', 'plan', 'subscription', 'interval'],
                filters={
                    "site": site_name,
                    "status": "Active",
                },
            )
            for app_sub in apps_sub:
                plan_app = frappe.get_doc("Plan", app_sub.get('plan'))
                if plan_app and team:
                    total_amount += plan_app.get_price_for_interval(
                        app_sub.get('interval'), team.currency)

            total_amount_vat = total_amount + (total_amount*vat/100)
            # tinh toan so tien truoc x ngay de canh bao
            total_prior_x = total_amount*x_day + (total_amount*x_day*vat/100)

            # luu lai so tien con lai khi su dung cua 1 site x ngay
            if balance_prior.get(team_name):
                amount_remaining_x = balance_prior[team_name] - total_prior_x
            else:
                # tinh so du kha dung sau khi su dung
                available_balances = team.available_balance()
                amount_remaining_x = available_balances - total_prior_x

            update_sub = True
            if amount_remaining_x >= 0:
                balance_prior[team_name] = amount_remaining_x
                # cap nhat lai so lan su dung bang 0
                subscription.estimated_number_of_notifications = 0
            else:
                number_warn = (
                    subscription.estimated_number_of_notifications or 0) + 1
                if number_warn <= num_advance_warning:
                    subscription.estimated_number_of_notifications = number_warn
                    send_email_handle_site('prior', site_name, team)
                else:
                    update_sub = False
            
            if update_sub:
                # cap nhat subscription
                subscription.save(ignore_permissions=True)
                frappe.db.commit()
                subscription.reload()
            
            update_sub = True
            # luu lai so tien con lai khi su dung cua 1 site
            if available_balances_team.get(team_name):
                amount_remaining = available_balances_team[team_name] - \
                    total_amount_vat
            else:
                # tinh so du kha dung sau khi su dung
                available_balances = team.available_balance()
                amount_remaining = available_balances - total_amount_vat
            # kiem tra su du
            if amount_remaining >= 0:
                available_balances_team[team_name] = amount_remaining
                # cap nhat lai so lan su dung bang 0
                subscription.number_days_used = 0
            else:
                # kiem tra so ngay de khoa site
                number_days_used = (subscription.number_days_used or 0) + 1
                if number_days_used > site_num_days_past_lock:
                    update_sub = False
                    # khoa site
                    reason = 'Khong du so du'
                    frappe.get_doc("Site", site_name).suspend(reason)
                    send_email_handle_site('lock', site_name, team)
                else:
                    # tang so lan su dung
                    subscription.number_days_used = number_days_used
                    send_email_handle_site('warning', site_name, team)

            if update_sub:
                # cap nhat subscription
                subscription.save(ignore_permissions=True)
                frappe.db.commit()
    except Exception as ex:
        frappe.db.rollback()
        log_error(title="Suspend site when account", name=str(ex))

def create_usage_records():
    """
    Creates daily usage records for paid Subscriptions
    """
    # truoc khi tao ho so su dung hang ngay kiem tra va khoa site
    suspend_site_when_account_balance_is_insufficient()

    free_sites = sites_with_free_hosting()
    subscriptions = frappe.db.get_all(
        "Subscription",
        filters={
            "enabled": True,
            "plan": ("in", paid_plans()),
            "name": ("not in", created_usage_records(free_sites)),
            "document_name": ("not in", free_sites),
        },
        pluck="name",
        limit=2000,
    )
    for name in subscriptions:
        subscription = frappe.get_cached_doc("Subscription", name)
        try:
            subscription.create_usage_record()
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            log_error(title="Create Usage Record Error", name=name)


def paid_plans():
    return frappe.db.get_all(
        "Plan",
        {
            "document_type": (
                "in",
                ("Site", "Server", "Database Server",
                 "Self Hosted Server", "Marketplace App"),
            ),
            "is_trial_plan": 0,
            "price_vnd": (">", 0),
        },
        pluck="name",
        ignore_ifnull=True,
    )


def sites_with_free_hosting():
    # sites marked as free
    free_sites = frappe.get_all(
        "Site",
        filters={"free": True, "status": (
            "not in", ("Archived", "Suspended"))},
        pluck="name",
    )

    marketplace_paid_plans = frappe.get_all(
        "Marketplace App Plan",
        {"is_free": 0, "standard_hosting_plan": ("is", "set")},
        pluck="name",
    )

    # sites with free/standard hosting (only for backward compatibility with smb plans)
    free_sites += frappe.get_all(
        "Marketplace App Subscription",
        {
            "marketplace_app_plan": ("in", marketplace_paid_plans),
            "status": "Active",
            "site": ("not in", free_sites),
        },
        pluck="site",
    )

    free_teams = frappe.get_all(
        "Team", filters={"free_account": True, "enabled": True}, pluck="name"
    )

    # sites owned by free_accounts that are not set as free sites
    free_sites += frappe.get_all(
        "Site",
        filters={
            "status": ("not in", ("Archived", "Suspended")),
            "team": ("in", free_teams),
            "name": ("not in", free_sites),
        },
        pluck="name",
    )

    return free_sites


def created_usage_records(free_sites, date=None):
    date = date or frappe.utils.today()
    """Returns created usage records for a particular date"""
    return frappe.get_all(
        "Usage Record",
        filters={
            "document_type": ("in", ("Site", "Server", "Database Server", "Self Hosted Server")),
            "date": date,
            "document_name": ("not in", free_sites),
        },
        pluck="subscription",
        ignore_ifnull=True,
    )


get_permission_query_conditions = get_permission_query_conditions_for_doctype(
    "Subscription"
)
