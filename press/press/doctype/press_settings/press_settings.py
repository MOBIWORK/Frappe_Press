# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import boto3
import frappe
from boto3.session import Session
from frappe.model.document import Document
from frappe.utils import get_url

from press.api.billing import get_stripe
from press.telegram_utils import Telegram
from press.utils import check_payos_settings

from payos import PayOS


class PressSettings(Document):
    @frappe.whitelist()
    def config_webhook_payos(self):
        client_id = self.payos_client_id
        api_key = self.payos_api_key
        checksum_key = self.payos_checksum_key
        payos_webhook_url = self.payos_webhook_url

        if not client_id or not api_key or not checksum_key:
            frappe.throw(
                'Vui lòng cấu hình đầy đủ thông tin Client Id, Api Key, Checksum Key để thực hiện thiết lập Webhook PayOs.')

        try:
            print('====')
            print(client_id)
            print(api_key)
            print(checksum_key)
            payOS = PayOS(client_id=client_id, api_key=api_key,
                          checksum_key=checksum_key)
            print(payOS)

            if not payos_webhook_url:
                frappe.throw(
                    'Vui lòng thêm đầy đủ thông tin Webhook Url để thực hiện thiết lập Webhook PayOs.')
            payos_webhook_url_current = payOS.confirmWebhook(payos_webhook_url)
            self.payos_webhook_url_current = payos_webhook_url_current
            self.save()
            self.reload()

            frappe.msgprint('Thiết lập Webhook PayOs thành công.')
        except Exception as ex:
            frappe.throw('Webhook Url không hợp lệ')

    @frappe.whitelist()
    def create_stripe_webhook(self):
        stripe = get_stripe()
        url = frappe.utils.get_url(
            "/api/method/press.press.doctype.stripe_webhook_log.stripe_webhook_log.stripe_webhook_handler"
        )
        webhook = stripe.WebhookEndpoint.create(
            url=url,
            enabled_events=[
                "payment_intent.requires_action",
                "payment_intent.payment_failed",
                "payment_intent.succeeded",
                "payment_method.attached",
                "invoice.payment_action_required",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
                "invoice.finalized",
            ],
        )
        self.stripe_webhook_endpoint_id = webhook["id"]
        self.stripe_webhook_secret = webhook["secret"]
        self.flags.ignore_mandatory = True
        self.save()

    @frappe.whitelist()
    def get_github_app_manifest(self):
        if frappe.conf.developer_mode:
            app_name = f"Frappe Cloud {frappe.generate_hash(length=6).upper()}"
        else:
            app_name = "Frappe Cloud"
        manifest = {
            "name": app_name,
            "url": "https://frappe.cloud",
            "hook_attributes": {"url": get_url("api/method/press.api.github.hook")},
            "redirect_url": get_url("github/redirect"),
            "description": "Managed Frappe Hosting",
            "public": True,
            "default_events": ["create", "push", "release"],
            "default_permissions": {"contents": "read"},
            # These keys aren't documented under the app creation from manifest
            # https://docs.github.com/en/free-pro-team@latest/developers/apps/creating-a-github-app-from-a-manifest
            # But are shown under app creation using url parameters
            # https://docs.github.com/en/free-pro-team@latest/developers/apps/creating-a-github-app-using-url-parameters
            # They seem to work. This might change later
            "callback_url": get_url("github/authorize"),
            "request_oauth_on_install": True,
            "setup_on_update": True,
        }
        return manifest

    @property
    def boto3_offsite_backup_session(self) -> Session:
        """Get new preconfigured boto3 session for offisite backup provider."""
        return Session(
            aws_access_key_id=self.offsite_backups_access_key_id,
            aws_secret_access_key=self.get_password(
                "offsite_backups_secret_access_key", raise_exception=False
            ),
            region_name="ap-south-1",
        )

    @property
    def boto3_iam_client(self):
        return boto3.client(
            "iam",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.get_password("aws_secret_access_key"),
        )

    @classmethod
    def is_offsite_setup(cls):
        return any(
            frappe.db.get_value(
                "Press Settings",
                "Press Settings",
                ["aws_s3_bucket", "offsite_backups_access_key_id"],
            )
        )

    @property
    def telegram(self):
        return Telegram
