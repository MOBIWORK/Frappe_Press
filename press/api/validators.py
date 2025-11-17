import frappe
import time
from functools import wraps


def validate_api_request(required_headers=None, api_key_required=False, rate_limit=None, token_auth=False):
    """
    Decorator để validate API request từ bên thứ ba
    
    Args:
        required_headers (list): Danh sách các header bắt buộc
        api_key_required (bool): Có yêu cầu API key không
        rate_limit (dict): Giới hạn số request (ví dụ: {"limit": 100, "window": 3600})
        token_auth (bool): Sử dụng Token authentication format (Token api_key:api_secret)
    
    Returns:
        decorator: Function decorator
    
    Example:
        @frappe.whitelist()
        @validate_api_request(
            required_headers=['User-Agent'],
            api_key_required=False,
            rate_limit={"limit": 100, "window": 3600}
        )
        def my_api_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_result = validate_request_headers(required_headers, api_key_required, token_auth)
            if not validation_result["success"]:
                return validation_result
            
            if rate_limit:
                rate_limit_result = check_rate_limit(rate_limit)
                if not rate_limit_result["success"]:
                    return rate_limit_result
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_request_headers(required_headers=None, api_key_required=False, token_auth=False):
    """
    Validate headers của request với hỗ trợ Token authentication
    
    Args:
        required_headers (list): Danh sách các header bắt buộc
        api_key_required (bool): Có yêu cầu API key không
        token_auth (bool): Sử dụng Token authentication format
        
    Returns:
        dict: {"success": bool, "message": str, "error_code": str}
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
                if not validate_token_auth(auth_header):
                    return {
                        "success": False,
                        "message": "Invalid Token format. Expected: Authorization: Token {api_key}:{api_secret}",
                        "error_code": "INVALID_TOKEN_FORMAT"
                    }
            else:
                # Legacy API key format
                api_key = headers.get('X-API-Key') or auth_header
                if not validate_api_key(api_key):
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


def validate_token_auth(auth_header):
    """
    Validate Token authentication format: "Token api_key:api_secret"
    
    Args:
        auth_header (str): Authorization header value
        
    Returns:
        bool: True if valid, False otherwise
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
        
        return True
    except Exception:
        return False


def validate_api_key(api_key):
    """
    Validate format của API key (legacy)
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        bool: True if valid, False otherwise
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


def check_rate_limit(rate_limit_config):
    """
    Kiểm tra rate limiting cho API
    
    Args:
        rate_limit_config (dict): {"limit": int, "window": int}
        
    Returns:
        dict: {"success": bool, "message": str, "error_code": str, "retry_after": int}
    
    Example:
        rate_limit_config = {"limit": 100, "window": 3600}  # 100 requests per hour
        result = check_rate_limit(rate_limit_config)
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


def validate_pagination_params(limit_start, limit_page_length, max_limit=1000):
    """
    Validate và normalize pagination parameters
    
    Args:
        limit_start: Vị trí bắt đầu
        limit_page_length: Số lượng bản ghi
        max_limit: Giới hạn tối đa cho limit_page_length
        
    Returns:
        tuple: (limit_start, limit_page_length)
    
    Example:
        limit_start, limit_page_length = validate_pagination_params(0, 20)
    """
    try:
        limit_start = int(limit_start)
        limit_page_length = int(limit_page_length)
        
        if limit_start < 0:
            limit_start = 0
            
        if limit_page_length <= 0 or limit_page_length > max_limit:
            limit_page_length = 20
            
        return limit_start, limit_page_length
    except (ValueError, TypeError):
        return 0, 20


def parse_filters(filters):
    """
    Parse và validate filters parameter
    
    Args:
        filters: String JSON, list, hoặc dict
        
    Returns:
        list or dict: Parsed filters
    
    Example:
        # From JSON string
        filters = parse_filters('[["status", "=", "Published"]]')
        
        # From dict
        filters = parse_filters({"status": "Published"})
    """
    import json
    
    if not filters:
        return []
    
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except json.JSONDecodeError:
            return []
    
    if not isinstance(filters, (list, dict)):
        return []
    
    return filters


def parse_fields(fields, default_fields=None):
    """
    Parse và validate fields parameter
    
    Args:
        fields: String JSON, list, hoặc wildcard "*"
        default_fields: Default fields nếu không có fields nào được chỉ định
        
    Returns:
        list: Parsed fields
    
    Example:
        # Wildcard
        fields = parse_fields("*")
        
        # JSON string
        fields = parse_fields('["name", "title", "status"]')
        
        # With default
        fields = parse_fields(None, default_fields=["name", "title"])
    """
    import json
    
    if not fields:
        return default_fields or ["*"]
    
    if isinstance(fields, str):
        if fields == "*":
            return ["*"]
        try:
            fields = json.loads(fields)
        except json.JSONDecodeError:
            return default_fields or ["*"]
    
    if not isinstance(fields, list):
        return default_fields or ["*"]
    
    return fields


def parse_boolean(value):
    """
    Parse boolean parameter từ string
    
    Args:
        value: String hoặc boolean value
        
    Returns:
        bool: Parsed boolean
    
    Example:
        parse_boolean("true")   # True
        parse_boolean("1")      # True
        parse_boolean("yes")    # True
        parse_boolean("false")  # False
        parse_boolean(True)     # True
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes']
    
    return False
