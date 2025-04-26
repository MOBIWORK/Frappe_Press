# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe import _
import json
from frappe.model.document import Document
from frappe.utils import random_string, get_url
from press.utils import get_country_info
from jinja2 import Template
from frappe.utils import fmt_money

class AccountRequest(Document):
    def before_insert(self):
        if not self.team:
            self.team = self.email

        if not self.request_key:
            self.request_key = random_string(32)

        self.ip_address = frappe.local.request_ip
        geo_location = self.get_country_info() or {}
        self.geo_location = json.dumps(geo_location, indent=1, sort_keys=True)
        self.state = geo_location.get("regionName")

        # check for US and EU
        if (
                geo_location.get("country") == "United States"
                or geo_location.get("continent") == "Europe"
        ):
            self.is_us_eu = True
        elif self.country == "United States":
            self.is_us_eu = True
        else:
            self.is_us_eu = False

    def after_insert(self):
        if self.send_email:
            self.send_verification_email()

    def get_country_info(self):
        return get_country_info()

    def too_many_requests_with_field(self, field_name, limits):
        key = getattr(self, field_name)
        for allowed_count, kwargs in limits:
            count = frappe.db.count(
                self.doctype,
                {field_name: key, "creation": (
                    ">", frappe.utils.add_to_date(None, **kwargs))},
            )
            if count > allowed_count:
                return True
        return False

    @frappe.whitelist()
    def send_verification_email(self):
        url = self.get_verification_url()

        # if frappe.conf.developer_mode:
        #     print(f"\nSetup account URL for {self.email}:")
        #     print(url)
        #     print()
        #     return

        pre_subject = "[MBWCloud] - "
        lang = self.language if self.language in ['vi', 'en'] else 'vi'
        
        free_credits_vnd = frappe.db.get_single_value("Press Settings", "free_credits_vnd") or 0
        money = fmt_money(free_credits_vnd, 0,"VND")
        subject = pre_subject + _('Verify your registered email {0}', lang).format(self.email)
        user_name = (self.first_name or '') + ' ' + (self.last_name or '')
        args = {
            'user_name': user_name,
            'app': self.saas_app or '',
            'money': money,
            'bonus': free_credits_vnd > 0
        }
        
        if self.subdomain:
            args['site_name'] = self.get_site_name()
            
        if self.saas_product:
            template = "saas_verify_account"
        else:
            template = "verify_account"

            if self.invited_by and self.role != "Press Admin":
                subject = pre_subject + _('You are invited by {0} to join MBWCloud', lang).format(self.invited_by)
                template = "invite_team_member"

        # get language template
        template = f"{lang}_{template}"
        
        args.update(
            {
                "invited_by": self.invited_by,
                "link": url,
                "image_path": "https://admin.mbwnext.com/assets/press/images/cropped-mbw.cloud_.10.png",
                "read_pixel_path": get_url(
                    f"/api/method/press.utils.telemetry.capture_read_event?name={self.name}"
                ),
            }
        )

        frappe.sendmail(
            recipients=self.email,
            subject=subject,
            template=template,
            args=args,
            now=True,
        )

    def get_verification_url(self):
        language = self.language or 'vi'
        if self.saas:
            return get_url(
                f"/api/method/press.api.saas.validate_account_request?key={self.request_key}&lang={language}"
            )

        return get_url(f"/dashboard/setup-account/{self.request_key}?lang={language}")

    @property
    def full_name(self):
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def get_site_name(self):
        return (
            self.subdomain + "." +
            frappe.db.get_value("Saas Settings", self.saas_app, "domain")
        )
