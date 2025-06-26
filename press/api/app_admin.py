import frappe
from frappe import _
import json
import time
from functools import wraps
from datetime import datetime, timedelta
from pypika.queries import QueryBuilder
from frappe.handler import run_doc_method as _run_doc_method
from press.utils import get_current_team_v2,get_current_team
from press.api.client import check_permissions, validate_fields, has_role,apply_custom_filters, validate_filters,get_list_query, check_document_access,fix_args,check_dashboard_actions,get
from press.press.doctype.marketplace_app.marketplace_app import get_plans_for_app
from press.api.site import is_marketplace_app_source, is_prepaid_marketplace_app
def validate_api_request(required_headers=None, api_key_required=False, rate_limit=None, token_auth=False):
    """
    Decorator để validate API request từ bên thứ ba
    
    Args:
        required_headers (list): Danh sách các header bắt buộc
        api_key_required (bool): Có yêu cầu API key không
        rate_limit (dict): Giới hạn số request (ví dụ: {"limit": 100, "window": 3600})
        token_auth (bool): Sử dụng Token authentication format (Token api_key:api_secret)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_result = _validate_request_headers(required_headers, api_key_required, token_auth)
            if not validation_result["success"]:
                return validation_result
            
            if rate_limit:
                rate_limit_result = _check_rate_limit(rate_limit)
                if not rate_limit_result["success"]:
                    return rate_limit_result
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _validate_request_headers(required_headers=None, api_key_required=False, token_auth=False):
    """
    Validate headers của request với hỗ trợ Token authentication
    """
    try:
        headers = frappe.local.request.headers if frappe.local.request else {}
        
        # Kiểm tra User-Agent để đảm bảo không phải bot độc hại
        user_agent = headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 5:
            return {
                "success": False,
                "message": "Invalid or missing User-Agent header",
                "error_code": "INVALID_USER_AGENT"
            }
        
        # Kiểm tra Content-Type cho POST requests
        if frappe.local.request and frappe.local.request.method == 'POST':
            content_type = headers.get('Content-Type', '')
            if 'application/json' not in content_type and 'application/x-www-form-urlencoded' not in content_type:
                return {
                    "success": False,
                    "message": "Invalid Content-Type. Expected application/json or application/x-www-form-urlencoded",
                    "error_code": "INVALID_CONTENT_TYPE"
                }
        
        # Kiểm tra Authentication nếu được yêu cầu
        if api_key_required:
            auth_header = headers.get('Authorization')
            if not auth_header:
                return {
                    "success": False,
                    "message": "Authorization header is required",
                    "error_code": "MISSING_AUTHORIZATION"
                }
            
            # Validate Token authentication format
            if token_auth:
                if not _validate_token_auth(auth_header):
                    return {
                        "success": False,
                        "message": "Invalid Token format. Expected: Authorization: Token {api_key}:{api_secret}",
                        "error_code": "INVALID_TOKEN_FORMAT"
                    }
            else:
                # Legacy API key format
                api_key = headers.get('X-API-Key') or auth_header
                if not _validate_api_key(api_key):
                    return {
                        "success": False,
                        "message": "Invalid API Key format",
                        "error_code": "INVALID_API_KEY"
                    }
        
        # Kiểm tra các header bắt buộc khác
        if required_headers:
            for header in required_headers:
                if header not in headers:
                    return {
                        "success": False,
                        "message": f"Required header '{header}' is missing",
                        "error_code": "MISSING_REQUIRED_HEADER"
                    }
        
        return {"success": True, "message": "Headers validation passed"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in header validation")
        return {
            "success": False,
            "message": "Header validation failed",
            "error_code": "VALIDATION_ERROR"
        }


def _validate_token_auth(auth_header):
    """
    Validate Token authentication format: "Token api_key:api_secret"
    """
    try:
        if not auth_header.startswith('Token '):
            return False
        
        token_part = auth_header[6:]  # Remove "Token "
        
        if ':' not in token_part:
            return False
        
        api_key, api_secret = token_part.split(':', 1)
        
        # Kiểm tra độ dài tối thiểu
        if len(api_key) < 10 or len(api_secret) < 10:
            return False
        
        # Có thể thêm logic kiểm tra trong database
        # return _check_api_credentials_in_db(api_key, api_secret)
        
        return True
    except Exception:
        return False


def _validate_api_key(api_key):
    """
    Validate format của API key (legacy)
    """
    try:
        # Loại bỏ "Bearer " nếu có
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Kiểm tra độ dài tối thiểu
        if not api_key or len(api_key) < 20:
            return False
        
        return True
    except:
        return False


def _check_rate_limit(rate_limit_config):
    """
    Kiểm tra rate limiting cho API
    """
    try:
        if not rate_limit_config:
            return {"success": True}
        
        limit = rate_limit_config.get("limit", 100)
        window = rate_limit_config.get("window", 3600)  # seconds
        
        # Lấy IP của client
        client_ip = frappe.local.request.environ.get('REMOTE_ADDR') if frappe.local.request else 'unknown'
        
        # Tạo key cho cache
        cache_key = f"rate_limit:{client_ip}:{frappe.local.request.path if frappe.local.request else 'unknown'}"
        
        # Lấy thông tin từ cache
        current_requests = frappe.cache().get(cache_key) or []
        current_time = time.time()
        
        # Loại bỏ các request cũ ngoài window
        current_requests = [req_time for req_time in current_requests if current_time - req_time < window]
        
        # Kiểm tra limit
        if len(current_requests) >= limit:
            return {
                "success": False,
                "message": f"Rate limit exceeded. Maximum {limit} requests per {window} seconds",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": window
            }
        
        # Thêm request hiện tại
        current_requests.append(current_time)
        frappe.cache().set(cache_key, current_requests, ex=window)
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in rate limiting")
        return {"success": True}  # Cho phép request nếu có lỗi trong rate limiting




# Áp dụng validation cho API hiện có
@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  # Có thể đổi thành True nếu muốn bắt buộc API key
    rate_limit={"limit": 100, "window": 3600}  # 100 requests per hour
)
def get_marketplace_app_plans():
    """
    REST API to fetch all Marketplace App Plans for third-party access.
    Đã được bảo vệ bởi validation layer.
    """
    try:
        plans = frappe.get_all(
            "Marketplace App Plan",
            fields=["name", "app", "price_inr", "price_usd"],
            order_by="creation desc"
        )

        return {
            "success": True,
            "message": "Marketplace App Plans fetched successfully",
            "data": plans,
            "count": len(plans)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_marketplace_app_plans")
        return {
            "success": False,
            "message": f"An error occurred while fetching Marketplace App Plans: {str(e)}",
            "data": [],
            "count": 0
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
@frappe.whitelist()
def get_emails():
	team = get_current_team_v2(get_doc=True)
	return [
		{
			"type": "billing_email",
			"value": team.billing_email,
		},
		{
			"type": "notify_email",
			"value": team.notify_email,
		},
	]


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def update_emails(data):
    from frappe.utils import validate_email_address
    try:
        # Nếu data là chuỗi JSON, chuyển đổi sang dictionary
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for data")
        data_convert = [
            {"type": "billing_email", "value": data.get("billing_email")},
            {"type": "notify_email", "value": data.get("notify_email")},
        ]
        
        data_dict = {item["type"]: item["value"] for item in data_convert}

        for _key, value in data_dict.items():
            validate_email_address(value, throw=True)

        # Lấy team document và cập nhật email
        team_doc = get_current_team_v2(get_doc=True)
        team_doc.billing_email = data_dict["billing_email"]
        team_doc.notify_email = data_dict["notify_email"]
        team_doc.save()

        return {
            "success": True,
            "message": "Emails updated successfully",
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in update_emails")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_site_information(site_name):
    """
    REST API to fetch site information details for third-party access.
    Returns detailed information about a site including owner, creation details, cluster info, and IP addresses.
    
    Args:
        site_name (str): Name of the site to get information for
    
    Returns:
        dict: Site information with success status and data
    """
    try:
        # Validate site name parameter
        if not site_name:
            return {
                "success": False,
                "message": "Site name is required",
                "error_code": "MISSING_SITE_NAME"
            }
        
        # Check if site exists and user has permission
        if not frappe.db.exists("Site", site_name):
            return {
                "success": False,
                "message": f"Site '{site_name}' not found",
                "error_code": "SITE_NOT_FOUND"
            }
        
        # Get site document with all required fields
        site_doc = frappe.get_doc("Site", site_name)
        
        # Get cluster information if exists
        cluster_info = {}
        if site_doc.get("cluster"):
            cluster_doc = frappe.get_doc("Cluster", site_doc.cluster)
            cluster_info = {
                "title": cluster_doc.get("title", ""),
                "image": cluster_doc.get("image", ""),
                "name": cluster_doc.name
            }
        
        # Prepare site information similar to frontend structure
        site_information = [
            {
                "label": "Owned by",
                "value": site_doc.get("owner_email", ""),
                "field": "owner_email"
            },
            {
                "label": "Created by", 
                "value": site_doc.get("signup_by") or site_doc.get("owner", ""),
                "field": "created_by"
            },
            {
                "label": "Created on",
                "value": site_doc.get("signup_time") or site_doc.get("creation", ""),
                "field": "created_on"
            },
            {
                "label": "Region",
                "value": cluster_info.get("title", ""),
                "field": "region",
                "cluster_image": cluster_info.get("image", ""),
                "cluster_name": cluster_info.get("name", "")
            },
            {
                "label": "Inbound IP",
                "value": site_doc.get("inbound_ip", ""),
                "field": "inbound_ip",
                "description": "Use this for adding A records for your site"
            },
            {
                "label": "Outbound IP", 
                "value": site_doc.get("outbound_ip", ""),
                "field": "outbound_ip",
                "description": "Use this for whitelisting our server on a 3rd party service"
            }
        ]
        
        # Additional site details
        site_details = {
            "name": site_doc.name,
            "status": site_doc.get("status", ""),
            "domain": site_doc.get("domain", ""),
            "subdomain": site_doc.get("subdomain", ""),
            "is_public": site_doc.get("is_public", False),
            "creation": site_doc.get("creation", ""),
            "modified": site_doc.get("modified", ""),
            "version": site_doc.get("version", ""),
            "current_plan": site_doc.get("current_plan", ""),
            "team": site_doc.get("team", "")
        }
        
        return {
            "success": True,
            "message": "Site information fetched successfully",
            "data": {
                "site_information": site_information,
                "site_details": site_details,
                "cluster": cluster_info
            }
        }
        
    except frappe.PermissionError:
        return {
            "success": False,
            "message": "Permission denied. You don't have access to this site",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_site_information")
        return {
            "success": False,
            "message": f"An error occurred while fetching site information: {str(e)}",
            "error_code": "FETCH_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def get_user_sites():
    """
    REST API to fetch all sites belonging to current user's team.
    Returns list of sites with basic information.
    
    Returns:
        dict: List of user's sites with success status
    """
    try:
        team = get_current_team()
        if not team:
            return {
                "success": False,
                "message": "No team found for current user",
                "error_code": "NO_TEAM_FOUND"
            }
        
        # Get all sites for the team
        sites = frappe.get_all(
            "Site",
            filters={"team": team},
            fields=[
                "name", "domain", "subdomain", "status", "creation", 
                "owner_email", "current_plan", "cluster", "version"
            ],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "message": "User sites fetched successfully",
            "data": {
                "sites": sites,
                "count": len(sites),
                "team": team
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_user_sites")
        return {
            "success": False,
            "message": f"An error occurred while fetching user sites: {str(e)}",
            "error_code": "FETCH_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def get_list(
	doctype: str,
	fields,
	filters ,
	order_by: str | None = None,
	start: int = 0,
	limit: int = 20,
	parent: str | None = None,
	debug: bool = False,
):
	# if filters is None:
	# 	filters = {}

	# Convert fields to list if it is a JSON string
	if isinstance(fields, str):
		try:
			fields = json.loads(fields)
			if not isinstance(fields, list):
				frappe.throw("Invalid format for fields. Expected a list.")
		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format for fields")

	# Convert filters to dict if it is a JSON string
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
			if not isinstance(filters, dict):
				frappe.throw("Invalid format for filters. Expected a dictionary.")
		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format for filters")

	# these doctypes doesn't have a team field to filter by but are used in get or run_doc_method
	if doctype in ["Team", "User SSH Key"]:
		return []

	check_permissions(doctype)
	valid_fields = validate_fields(doctype, fields)
	valid_filters = validate_filters(doctype, filters)

	meta = frappe.get_meta(doctype)
	if meta.istable and not (filters.get("parenttype") and filters.get("parent")):
		frappe.throw("parenttype and parent are required to get child records")

	apply_team_filter = not (
		filters.get("skip_team_filter_for_system_user_and_support_agent")
		and (frappe.local.system_user() or has_role("Press Support Agent"))
	)
	if apply_team_filter and meta.has_field("team"):
		valid_filters.team = frappe.local.team().name

	query = get_list_query(
		doctype,
		meta,
		filters,
		valid_filters,
		valid_fields,
		start,
		limit,
		order_by,
	)
	filters = frappe._dict(filters or {})
	list_args = dict(
		fields=fields,
		filters=filters,
		order_by=order_by,
		start=start,
		limit=limit,
		parent=parent,
		debug=debug,
	)
	query = apply_custom_filters(doctype, query, **list_args)
	if isinstance(query, QueryBuilder):
		return query.run(as_dict=1, debug=debug)

	if isinstance(query, list):
		return query

	return []

@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def available_apps(name):
	site = frappe.get_doc("Site", name)

	installed_apps = [app.app for app in site.apps]

	bench = frappe.get_doc("Bench", site.bench)
	bench_sources = [app.source for app in bench.apps]

	available_sources = []

	AppSource = frappe.qb.DocType("App Source")
	MarketplaceApp = frappe.qb.DocType("Marketplace App")

	sources = (
		frappe.qb.from_(AppSource)
		.left_join(MarketplaceApp)
		.on(AppSource.app == MarketplaceApp.app)
		.select(
			AppSource.name,
			AppSource.app,
			AppSource.repository_url,
			AppSource.repository_owner,
			AppSource.branch,
			AppSource.team,
			AppSource.public,
			AppSource.app_title,
			MarketplaceApp.title,
		)
		.where(AppSource.name.isin(bench_sources))
		.run(as_dict=True)
	)

	for source in sources:
		frappe_version = frappe.db.get_value("Release Group", bench.group, "version")

		if is_marketplace_app_source(source.name):
			app_plans = get_plans_for_app(source.app, frappe_version)
			source.billing_type = is_prepaid_marketplace_app(source.app)
		else:
			app_plans = []

		if len(app_plans) > 0:
			source.has_plans_available = True
			source.plans = app_plans

		if source.app not in installed_apps:
			available_sources.append(source)

	return sorted(available_sources, key=lambda x: bench_sources.index(x.name))

