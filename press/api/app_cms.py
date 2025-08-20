import frappe
import requests
import json


@frappe.whitelist(allow_guest=True)
def get_template(template_name = None,api_key=None, api_secret=None,base_url=None):
	try:
		base_url = base_url
		api_key = api_key
		api_secret = api_secret
		if not base_url or not api_key or not api_secret:
			frappe.log_error(f"Call func cms error", "Base URL, api_key, api_secret is not configured.")
			return
		api_endpoint = f"{base_url}/api/method/mbw_cms.api.mbw_website_template.create_client_website" 
		data = {
			"name": template_name,
		}
		res = requests.post(
			api_endpoint,
			json=data,
			headers={
				"Content-Type": "application/json",	
				"Authorization": f"Token {api_key}:{api_secret}"
			}
		).json()

		return res
	except Exception as e:
		frappe.log_error(f"Call Api CMS Failed: {e}")

@frappe.whitelist(allow_guest=True)
def get_site_api_credentials(site_name):
	"""
	Get API key and secret from site config of mbw_cms app using get_key_config endpoint
	"""
	try:
		print('vào đây 2>>>>>>>>>>>>>>')
		print(f"site_name: {site_name}")
		# Ensure site_name has protocol
		if not site_name.startswith(('http://', 'https://')):
			site_name = f"https://{site_name}"
		
		api_endpoint = f"{site_name}/api/method/mbw_cms.api.mbw_website_template.get_key_config"
		response = requests.post(
			api_endpoint,
			headers={
				"Content-Type": "application/json"
			},
			timeout=10 
		)
		
		if response.status_code == 200:
			response_data = response.json()
			
			if response_data.get("message"):
				config_data = response_data["message"]
				api_key = config_data.get("admin_api_key")
				api_secret = config_data.get("admin_api_secret")
				
				if api_key and api_secret:
					return {
						"success": True,
						"api_key": api_key,
						"api_secret": api_secret,
						"debug_text": config_data.get("text", "")
					}
				else:
					return {
						"success": False,
						"message": "API key or secret not found in response",
						"response_data": config_data
					}
			else:
				return {
					"success": False,
					"message": "Invalid response format from get_key_config",
					"response_data": response_data
				}
		else:
			return {
				"success": False,
				"message": f"Failed to fetch API credentials: HTTP {response.status_code}"
			}
			
	except Exception as e:
		return {
			"success": False,
			"message": f"Exception occurred: {str(e)}"
		}


@frappe.whitelist(allow_guest=True)
def handle_cms_site_creation(site_name=None, product_id=None, subdomain=None, template_name=None):
	"""
	Handle CMS site creation - call get_template after site is created with go1_cms or mbw_cms
	"""
	try:
		print('Đã vào hàm handle_cms_site_creation >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		print(f"site_name: {site_name}, product_id: {product_id}, subdomain: {subdomain}, template_name: {template_name}")
		if product_id not in ['go1_cms', 'mbw_cms']:
			return {
				"success": False,
				"message": "Not a CMS app"
			}
		
		# Construct base URL
		base_url = f"https://{subdomain}.nhansu360.com"
		print(f"base_url>>>>>>>>: {base_url}")
		
		# Get API credentials from the created site
		credentials = get_site_api_credentials(f"{subdomain}.nhansu360.com")
		print(f"credentials>>>>>>>>: {credentials}")
		if not credentials.get("success"):
			frappe.log_error(f"Failed to get API credentials for {site_name}")
			return credentials
		
		api_key = credentials.get("api_key")
		api_secret = credentials.get("api_secret")
		
		if not api_key or not api_secret:
			return {
				"success": False,
				"message": "API key or secret not found in site config"
			}
		# Call get_template function
		template_result = get_template(
			template_name=template_name,
			api_key=api_key,
			api_secret=api_secret,
			base_url=base_url
		)
		frappe.log_error(f"CMS site creation handled for {site_name}: {template_result}", "CMS Site Creation")
		
		return {
			"success": True,
			"message": "CMS site creation handled successfully",
			"template_result": template_result
		}
		
	except Exception as e:
		frappe.log_error(f"Error handling CMS site creation: {e}")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}


@frappe.whitelist(allow_guest=True)
def get_cms_template_list(page_length=20, page_start=0, filters=None, order_by="modified asc"):
	"""
	Get list of CMS Manage Template records with pagination and filtering
	"""
	try:
		# Parse filters if provided as string
		if isinstance(filters, str):
			filters = json.loads(filters)
		
		# Get records using get_list with pagination
		templates = frappe.get_list(
			"CMS Manage Template",
			fields=["name", "template_id", "template_name", "image_template", "creation", "modified"],
			filters=filters or {},
			order_by=order_by,
			limit_page_length=page_length,
			limit_start=page_start
		)
		
		# Get total count for pagination
		total_count = frappe.db.count("CMS Manage Template", filters=filters or {})
		
		# Format the response
		formatted_templates = []
		for template in templates:
			formatted_template = {
				"id": template.name,
				"template_id": template.template_id,
				"template_name": template.template_name,
				"image_template": template.image_template,
				"created_at": template.creation,
				"updated_at": template.modified
			}
			formatted_templates.append(formatted_template)
		
		return {
			"success": True,
			"data": formatted_templates,
			"total": total_count,
			"page_length": page_length,
			"page_start": page_start
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting CMS template list: {e}")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}

