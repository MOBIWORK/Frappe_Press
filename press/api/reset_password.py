from __future__ import annotations

import requests

import frappe
from frappe.utils.data import sha256_hash
from frappe.utils import now_datetime, get_url
from press.api.client import dashboard_whitelist


def generate_reset_password_link(site_name: str, domain: str, product_trial: str, target_user: str) -> str:
	"""
	Tạo đường dẫn tới trang đổi mật khẩu tùy chỉnh.
	Trang này sẽ cho phép user đổi mật khẩu và redirect tới setup wizard.
	"""
	# Return dashboard URL pointing to custom Vue reset form
	reset_page_path = f"/dashboard/create-site/{product_trial}/reset-password"
	base = get_url(reset_page_path)
	return f"{base}?domain={domain}&user={target_user}"


@dashboard_whitelist()
def get_reset_password_link() -> str:
	"""
	Dashboard-accessible API to return reset-password URL for a given
	Product Trial Request.
	"""
	product_trial_request = frappe.form_dict.get('product_trial_request')
	if not product_trial_request:
		frappe.throw("product_trial_request parameter is required")
	
	ptr = frappe.get_doc("Product Trial Request", product_trial_request)
	if not ptr.site or not ptr.domain:
		frappe.throw("Site or domain not set on Product Trial Request")
	team_user = frappe.db.get_value("Team", ptr.team, "user")
	if not team_user:
		frappe.throw("Team user not found")
	
	try:
		frappe.log_error(
			"Reset Password Debug",
			f"Starting get_reset_password_link for PTR: {product_trial_request}, site: {ptr.site}, domain: {ptr.domain}, team_user: {team_user}",
		)
		reset_url = generate_reset_password_link(ptr.site, ptr.domain, ptr.product_trial, target_user=team_user)
		frappe.log_error(
			"Reset Password Debug",
			f"Reset password URL generated successfully",
		)
		return reset_url
	except Exception as e:
		frappe.log_error("Reset Password Error", f"Error generating reset password link: {str(e)}")
		raise


@dashboard_whitelist(allow_guest=True, methods=["POST"])
def update_password_direct(domain: str, user: str, new_password: str, confirm_password: str) -> str:
	"""
	Đổi mật khẩu trực tiếp cho user và redirect tới setup wizard.
	Cách đơn giản: đổi mật khẩu trong database rồi redirect.
	"""
	if not domain or not user or not new_password or not confirm_password:
		frappe.throw("Missing required parameters for password update.")

	if new_password != confirm_password:
		frappe.throw("Passwords do not match.")

	try:
		# Login as admin to the target site
		from press.press.doctype.site.site import Site
		site: Site = frappe.get_doc("Site", domain)
		admin_sid = site.get_login_sid(user="Administrator")
		headers = {"Cookie": f"sid={admin_sid}"}

		# Update password directly using frappe.client.set_value
		response = requests.post(
			f"https://{domain}/api/method/frappe.client.set_value",
			headers=headers,
			data={
				"doctype": "User",
				"name": user,
				"fieldname": "new_password",
				"value": new_password,
			},
			timeout=20,
		)
		
		if not response.ok:
			frappe.log_error("Reset Password Error", f"Failed to update password: {response.status_code} - {response.text}")
			frappe.throw("Failed to update password. Please try again.")

		# Get login SID for the user after password change
		user_sid = site.get_login_sid(user=user)
		
		# Return URL to setup wizard with SID
		return f"https://{domain}/app/setup-wizard/0?sid={user_sid}"

	except Exception as e:
		frappe.log_error("Reset Password Error", f"Error updating password: {str(e)}")
		frappe.throw(f"Failed to update password: {str(e)}")


