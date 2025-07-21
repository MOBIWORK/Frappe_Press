import frappe
import requests
import json

@frappe.whitelist(allow_guest=True)
def post_template(template_name = None):
	api_key = "5deed33f5858d09"
	api_secret = "683d0a191abb537"
	print("=---------------", f"Token {api_key}:{api_secret}")
	try:
		url = f"http://localhost:8080/api/method/go1_cms.api.mbw_website_template.prepare_file_template"
		headers = {
			"Authorization": f"Token {api_key}:{api_secret}",
			"Content-Type": "application/json"
		}
		response = requests.post(url, headers=headers, timeout=30)
		print("=---------------", response.json())
		return response.json()

	except Exception as e:
		return {
			"success": False,
			"message": f"Error: {str(e)}",
			"error_code": "REQUEST_FAILED"
		}

@frappe.whitelist(allow_guest=True)
def get_template(template_name = None):
	try:
		base_url = frappe.conf.get("go1_cms_site_name") or 'http://localhost:8080'
		api_key = frappe.conf.get("go1_cms_api_key") or '5deed33f5858d09'
		api_secret = frappe.conf.get("go1_cms_api_secret") or '683d0a191abb537'
		if not base_url or not api_key or not api_secret:
			frappe.log_error(f"Call func cms error", "Base URL, api_key, api_secret is not configured.")
			return
		api_endpoint = base_url + "/api/method/go1_cms.api.mbw_website_template.prepare_file_template"
		data = {
			"template_name": template_name,
		}
		res = requests.post(
			api_endpoint,
			json=data,
			headers={
				"Content-Type": "application/json",
				"Authorization": f"Token {api_key}:{api_secret}"
			}
		)
		return res.json()
	except Exception as e:
		frappe.log_error(f"Call Api CMS Failed: {e}")