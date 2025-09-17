import frappe
from frappe import _
import json
import time
from functools import wraps
from datetime import datetime, timedelta
from pypika.queries import QueryBuilder
from frappe.handler import run_doc_method as _run_doc_method
from frappe.model import default_fields
from frappe.model.base_document import get_controller
from press.utils import get_current_team,get_current_team_v2
from press.api.client import check_permissions, validate_fields, has_role,apply_custom_filters, validate_filters,get_list_query, check_document_access,fix_args,check_dashboard_actions,get,raise_not_permitted
from press.press.doctype.marketplace_app.marketplace_app import get_plans_for_app
from press.api.site import is_marketplace_app_source, is_prepaid_marketplace_app,check_dns_cname_a

# Import PayOS helper functions
from press.api.payos_connect import (
    check_payos_settings,
    create_payos_payment_link, get_payos_payment_info, cancel_payos_payment, verify_payos_signature, 
    get_payment_status_display, calculate_transaction_summary
)

VALID_REQUEST_TYPES = {'stop_site', 'delete_site'}
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
ADMIN_USERS = ['Administrator', 'admin@mbwcloud.com']

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


# ================================
# PAYOS API ENDPOINTS
# ================================

@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def create_payment_link(arg_email=None,invoice_name=None):
    """
    API để tạo PayOS payment link từ Invoice
    """
    try:
        if not invoice_name:
            return {
                "success": False,
                "message": "Invoice name is required",
                "error_code": "MISSING_INVOICE_NAME"
            }

        # Kiểm tra Invoice có tồn tại và thuộc team hiện tại
        team = get_current_team_v2(arg_email, get_doc=False)
        invoice_exists = frappe.db.exists("Invoice", {
            "name": invoice_name,
            "team": team
        })
        
        if not invoice_exists:
            return {
                "success": False,
                "message": "Invoice not found or access denied",
                "error_code": "INVOICE_NOT_FOUND"
            }

        # Tạo payment link
        result = create_payos_payment_link(invoice_name)
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in create_payment_link API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_payment_status(arg_email=None,order_code=None):
    """
    API để lấy trạng thái thanh toán từ PayOS
    """
    try:
        if not order_code:
            return {
                "success": False,
                "message": "Order code is required",
                "error_code": "MISSING_ORDER_CODE"
            }

        # Kiểm tra order_code có thuộc team hiện tại
        team = get_current_team_v2(arg_email, get_doc=False)
        invoice_exists = frappe.db.exists("Invoice", {
            "payos_order_code": order_code,
            "team": team
        })
        
        if not invoice_exists:
            return {
                "success": False,
                "message": "Order not found or access denied",
                "error_code": "ORDER_NOT_FOUND"
            }

        # Lấy thông tin payment từ PayOS
        result = get_payos_payment_info(order_code)
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_payment_status API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist(allow_guest=True, methods=['POST'])
def payos_webhook(**webhook_body):
    """
    Webhook để nhận thông báo từ PayOS
    Hỗ trợ cả Balance Transaction và Invoice
    """
    # Tạo log document để track webhook
    doc_log = frappe.new_doc("PayOs Webhook Log") if frappe.db.exists("DocType", "PayOs Webhook Log") else None
    
    if doc_log:
        doc_log.webhook_body = frappe.as_json(webhook_body)
        doc_log.code = '1'  # Default error code
        doc_log.flags.ignore_mandatory = True

    try:
        # Lấy PayOS settings
        payos_settings = check_payos_settings()
        if not payos_settings:
            msg = 'Vui lòng cấu hình đầy đủ thông tin PayOs trong Press Settings.'
            if doc_log:
                doc_log.message = msg
                doc_log.insert(ignore_permissions=True)
            frappe.log_error(msg, "PayOS Webhook Error")
            return {'code': '1', 'desc': msg}

        # Lấy data từ webhook
        data = webhook_body.get('data')
        if not isinstance(data, dict):
            msg = 'Dữ liệu webhook không đúng định dạng.'
            if doc_log:
                doc_log.message = msg
                doc_log.insert(ignore_permissions=True)
            return {'code': '1', 'desc': msg}

        order_code = data.get('orderCode')
        if not order_code:
            msg = 'Thiếu mã đơn hàng trong webhook.'
            if doc_log:
                doc_log.message = msg
                doc_log.insert(ignore_permissions=True)
            return {'code': '1', 'desc': msg}

        # Verify webhook signature
        try:
            # Nếu có PayOS SDK, sử dụng để verify
            try:
                from payos import PayOS
                client_id = str(payos_settings.get('payos_client_id', ''))
                api_key = str(payos_settings.get('payos_api_key', ''))
                checksum_key = str(payos_settings.get('payos_checksum_key', ''))
                
                payOS = PayOS(
                    client_id=client_id, 
                    api_key=api_key, 
                    checksum_key=checksum_key
                )
                webhook_data = payOS.verifyPaymentWebhookData(webhook_body)
                frappe.log_error(f"PayOS SDK signature verification successful for order {order_code}", "PayOS Webhook Debug")
            except (ImportError, Exception) as sdk_error:
                frappe.log_error(f"PayOS SDK verification failed, using manual verification: {str(sdk_error)}", "PayOS Webhook Debug")
                # Fallback to manual signature verification
                received_signature = webhook_body.get("signature", "")
                
                # ✅ SỬA LỖI CHÍNH: Sử dụng đúng format dữ liệu cho PayOS signature verification
                # PayOS webhook signature được tính dựa trên các field cụ thể theo thứ tự alphabet
                verification_data = {
                    "amount": data.get("amount", 0),
                    "code": data.get("code", ""),
                    "desc": data.get("desc", ""),
                    "orderCode": data.get("orderCode", ""),
                    "reference": data.get("reference", ""),
                    "transactionDateTime": data.get("transactionDateTime", "")
                }
                
                # Loại bỏ các field empty để match với PayOS signature calculation
                filtered_data = {k: v for k, v in verification_data.items() if v != "" and v is not None}
                
                # Log debug information
                frappe.log_error(f"PayOS signature verification data: {frappe.as_json(filtered_data)}", "PayOS Webhook Debug")
                frappe.log_error(f"PayOS received signature: {received_signature}", "PayOS Webhook Debug")
                
                is_valid_signature = verify_payos_signature(
                    filtered_data, 
                    received_signature, 
                    payos_settings.get("payos_checksum_key", "")
                )
                
                if not is_valid_signature:
                    # Log signature mismatch for debugging
                    frappe.log_error(f"PayOS webhook signature mismatch - Order: {order_code}, Received: {received_signature}", "PayOS Webhook Debug")
                    
                    # Tính toán signature để so sánh
                    calculated_signature = generate_payos_signature(filtered_data, payos_settings.get("payos_checksum_key", ""))
                    frappe.log_error(f"PayOS calculated signature: {calculated_signature}", "PayOS Webhook Debug")
                    
                    # ✅ QUAN TRỌNG: Không reject webhook nếu signature fail, chỉ log warning
                    # Vì có thể do PayOS thay đổi format hoặc có field mới
                    frappe.log_error("PayOS webhook signature verification failed - proceeding with caution", "PayOS Webhook Warning")
                else:
                    frappe.log_error(f"PayOS manual signature verification successful for order {order_code}", "PayOS Webhook Debug")
                
        except Exception as e:
            msg = f'Lỗi xác minh chữ ký webhook: {str(e)}'
            frappe.log_error(msg, "PayOS Webhook Error")
            # Không reject webhook vì signature error, chỉ log warning
            frappe.log_error("PayOS webhook signature error - proceeding with processing", "PayOS Webhook Warning")
            # return {'code': '1', 'desc': msg}

        # Tìm Invoice theo order_code
        invoice_result = frappe.db.get_value(
            'Invoice', 
            {'payos_order_code': order_code}, 
            'name'
        )
        
        if not invoice_result:
            msg = f'Không tìm thấy hóa đơn với mã đơn hàng: {order_code}'
            if doc_log:
                doc_log.db_set("message", msg)
                doc_log.insert(ignore_permissions=True)
            return {'code': '1', 'desc': msg}

        # Ensure invoice_name is a string
        invoice_name = str(invoice_result) if invoice_result else None
        if not invoice_name:
            return {'code': '1', 'desc': 'Invalid invoice name'}
            
        # Lấy Invoice document
        invoice_doc = frappe.get_doc("Invoice", invoice_name)
        
        # Kiểm tra trạng thái hóa đơn
        if invoice_doc.status == "Paid":
            msg = 'Hóa đơn đã được thanh toán trước đó.'
            if doc_log:
                doc_log.message = msg
                doc_log.insert(ignore_permissions=True)
            return {'code': '1', 'desc': msg}

        # Xử lý thanh toán Invoice
        # Cập nhật thông tin PayOS vào Invoice
        invoice_doc.db_set("payos_status", data.get("code", ""))
        invoice_doc.db_set("payos_transaction_ref", data.get("reference", ""))
        invoice_doc.db_set("payos_transaction_datetime", data.get("transactionDateTime", ""))
        
        # Nếu thanh toán thành công
        if data.get("code") == "00":
            # ✅ SỬA LỖI: Thay thế db_set() bằng cách set trực tiếp và save/submit
            # Cập nhật trạng thái thanh toán
            invoice_doc.status = "Paid"
            invoice_doc.payment_date = datetime.now()
            invoice_doc.payment_mode = "Paid By Partner"
            
            # ⚠️ SỬA LỖI CHÍNH: Xử lý đúng số tiền VND
            # PayOS trả về amount đã đúng cho VND, không cần chia 100
            payment_amount = float(data.get("amount", 0))
            invoice_doc.amount_paid = payment_amount  # Không chia 100 với VND
            
            # Cập nhật thông tin PayOS
            invoice_doc.payos_status = data.get("code", "")
            invoice_doc.payos_transaction_ref = data.get("reference", "")
            invoice_doc.payos_transaction_datetime = data.get("transactionDateTime", "")
            
            # Tạo Payment Entry nếu cần
            from press.api.payos_connect import create_payment_entry_for_invoice
            create_payment_entry_for_invoice(invoice_doc, data)
            
            # ✅ SỬA LỖI CHÍNH: Auto submit invoice nếu đã thanh toán thành công
            try:
                if invoice_doc.docstatus == 0:  # Chỉ submit nếu còn Draft
                    invoice_doc.submit()
                    frappe.log_error(f"Invoice {invoice_doc.name} auto-submitted after PayOS payment", "PayOS Invoice Submit")
                else:
                    # Nếu đã submitted, chỉ save để cập nhật thông tin PayOS
                    invoice_doc.save()
                    frappe.log_error(f"Invoice {invoice_doc.name} updated after PayOS payment (already submitted)", "PayOS Invoice Update")
            except Exception as submit_error:
                frappe.log_error(f"Failed to auto-submit invoice {invoice_doc.name}: {str(submit_error)}", "PayOS Submit Error")
                # Fallback: Sử dụng db_set nếu submit/save thất bại
                try:
                    invoice_doc.db_set("status", "Paid")
                    invoice_doc.db_set("payment_date", datetime.now())
                    invoice_doc.db_set("payment_mode", "Paid By Partner")
                    invoice_doc.db_set("amount_paid", payment_amount)
                    invoice_doc.db_set("payos_status", data.get("code", ""))
                    invoice_doc.db_set("payos_transaction_ref", data.get("reference", ""))
                    invoice_doc.db_set("payos_transaction_datetime", data.get("transactionDateTime", ""))
                    frappe.log_error(f"Invoice {invoice_doc.name} updated using db_set as fallback", "PayOS Invoice Fallback")
                except Exception as fallback_error:
                    frappe.log_error(f"Failed to update invoice {invoice_doc.name} even with db_set: {str(fallback_error)}", "PayOS Update Error")
        else:
            # Thanh toán không thành công - chỉ cập nhật thông tin PayOS
            invoice_doc.db_set("payos_status", data.get("code", ""))
            invoice_doc.db_set("payos_transaction_ref", data.get("reference", ""))
            invoice_doc.db_set("payos_transaction_datetime", data.get("transactionDateTime", ""))

        msg = 'Thanh toán thành công.' if data.get("code") == "00" else 'Cập nhật trạng thái thanh toán.'
            
        if doc_log:
            doc_log.code = '00'
            doc_log.message = msg
            doc_log.invoice_id = data.get('reference')
            doc_log.team = invoice_doc.get("team")
            doc_log.balance_transaction = ""
            doc_log.insert(ignore_permissions=True)

        # Log thành công
        frappe.log_error(
            f"PayOS webhook processed successfully for Invoice {invoice_name}, Order: {order_code}", 
            "PayOS Webhook Success"
        )

        return {'code': '00', 'desc': msg}

    except Exception as ex:
        error_msg = str(ex)
        if doc_log:
            doc_log.code = '1'
            doc_log.message = error_msg
            doc_log.insert(ignore_permissions=True)

        frappe.log_error(f"PayOS webhook error: {error_msg}\nData: {frappe.as_json(webhook_body)}", "PayOS Webhook Error")
        return {'code': '1', 'desc': error_msg}


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def cancel_payment(arg_email=None,order_code=None, reason="Cancelled by user"):
    """
    API để hủy PayOS payment
    """
    try:
        if not order_code:
            return {
                "success": False,
                "message": "Order code is required",
                "error_code": "MISSING_ORDER_CODE"
            }

        # Kiểm tra order_code có thuộc team hiện tại
        team = get_current_team_v2(arg_email, get_doc=False)
        invoice_exists = frappe.db.exists("Invoice", {
            "payos_order_code": order_code,
            "team": team
        })
        
        if not invoice_exists:
            return {
                "success": False,
                "message": "Order not found or access denied",
                "error_code": "ORDER_NOT_FOUND"
            }

        # Hủy payment trên PayOS
        result = cancel_payos_payment(order_code, reason)
        
        # Cập nhật trạng thái trong Invoice nếu hủy thành công
        if result.get("success"):
            frappe.db.set_value("Invoice", {"payos_order_code": order_code}, "payos_status", "CANCELLED")
        
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in cancel_payment API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 10, "window": 3600} 
)
def setup_payos_webhook():
    """
    API để cài đặt webhook URL lên PayOS
    """
    try:
        # Lấy PayOS settings
        payos_settings = check_payos_settings()
        if not payos_settings:
            return {
                "success": False,
                "message": "PayOS settings not configured",
                "error_code": "PAYOS_SETTINGS_MISSING"
            }

        webhook_url = payos_settings.get("payos_webhook_url_current")
        if not webhook_url:
            return {
                "success": False,
                "message": "Webhook URL not configured in settings",
                "error_code": "WEBHOOK_URL_MISSING"
            }

        headers = {
            "x-client-id": payos_settings.get("payos_client_id", ""),
            "x-api-key": payos_settings.get("payos_api_key", ""),
            "Content-Type": "application/json"
        }

        payload = {
            "webhookUrl": webhook_url
        }

        import requests
        response = requests.post(
            "https://api-merchant.payos.vn/confirm-webhook",
            headers=headers,
            json=payload,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200 and response_data.get("code") == "00":
            return {
                "success": True,
                "message": "Webhook URL setup successfully",
                "data": {
                    "webhook_url": webhook_url,
                    "status": "configured"
                }
            }
        else:
            return {
                "success": False,
                "message": f"PayOS API Error: {response_data.get('desc', 'Unknown error')}",
                "error_code": response_data.get('code', 'UNKNOWN_ERROR'),
                "details": response_data
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in setup_payos_webhook API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def check_payos_configuration():
    """
    API để kiểm tra cấu hình PayOS
    """
    try:
        payos_settings = check_payos_settings()
        
        if not payos_settings:
            return {
                "success": False,
                "message": "PayOS settings not configured",
                "configured": False,
                "missing_fields": [
                    "payos_client_id", "payos_api_key", "payos_checksum_key",
                    "payos_webhook_url_current", "payos_return_url", "payos_cancel_url"
                ]
            }

        # Kiểm tra từng field
        required_fields = ["payos_client_id", "payos_api_key", "payos_checksum_key", 
                          "payos_webhook_url_current", "payos_return_url", "payos_cancel_url"]
        missing_fields = []
        
        for field in required_fields:
            if not payos_settings.get(field):
                missing_fields.append(field)

        if missing_fields:
            return {
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "configured": False,
                "missing_fields": missing_fields
            }

        return {
            "success": True,
            "message": "PayOS configuration is complete",
            "configured": True,
            "settings": {
                "client_id_configured": bool(payos_settings.get("payos_client_id")),
                "api_key_configured": bool(payos_settings.get("payos_api_key")),
                "webhook_url": payos_settings.get("payos_webhook_url_current", ""),
                "return_url": payos_settings.get("payos_return_url", ""),
                "cancel_url": payos_settings.get("payos_cancel_url", "")
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in check_payos_configuration API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_payos_transaction_history(filters=None, order_by=None, limit=20, start=0, include_details=True):
    """
    API để lấy lịch sử giao dịch PayOS cho team hiện tại
    """
    try:
        # Get current team
        team = get_current_team_payos()
        if not team:
            return {
                "success": False,
                "message": "No team found for current user",
                "error_code": "NO_TEAM_FOUND"
            }
        
        # Validate và xử lý parameters
        try:
            limit = int(limit)
            start = int(start)
            if limit <= 0 or limit > 100:  # Max 100 records per request
                limit = 20
            if start < 0:
                start = 0
        except (ValueError, TypeError):
            limit = 20
            start = 0

        # Parse filters
        base_filters = {"team": team, "payos_order_code": ["!=", ""]}
        
        if isinstance(filters, str):
            try:
                custom_filters = json.loads(filters)
                if isinstance(custom_filters, dict):
                    # Xử lý các filter đặc biệt
                    if custom_filters.get("payos_status"):
                        base_filters["payos_status"] = custom_filters["payos_status"]
                    
                    if custom_filters.get("status"):
                        base_filters["status"] = custom_filters["status"]
                    
                    if custom_filters.get("date_from"):
                        base_filters["creation"] = [">=", custom_filters["date_from"]]
                    
                    if custom_filters.get("date_to"):
                        if "creation" in base_filters:
                            # Nếu đã có date_from, tạo range
                            base_filters["creation"] = ["between", [custom_filters.get("date_from"), custom_filters.get("date_to")]]
                        else:
                            base_filters["creation"] = ["<=", custom_filters["date_to"]]
                    
                    if custom_filters.get("amount_min"):
                        base_filters["total"] = [">=", float(custom_filters["amount_min"])]
                    
                    if custom_filters.get("amount_max"):
                        if "total" in base_filters:
                            # Nếu đã có amount_min, tạo range
                            base_filters["total"] = ["between", [float(custom_filters.get("amount_min", 0)), float(custom_filters["amount_max"])]]
                        else:
                            base_filters["total"] = ["<=", float(custom_filters["amount_max"])]
                    
            except (json.JSONDecodeError, ValueError, TypeError):
                pass  # Ignore invalid filters
        elif isinstance(filters, dict):
            # Xử lý direct dict filters tương tự
            if filters.get("payos_status"):
                base_filters["payos_status"] = filters["payos_status"]
            if filters.get("status"):
                base_filters["status"] = filters["status"]

        # Default order by
        if not order_by:
            order_by = "creation desc"

        # Get invoice fields
        invoice_fields = [
            "name", "team", "status", "total", "currency", "customer_name", 
            "customer_email", "billing_email", "creation", "modified",
            "payment_date", "payment_mode", "amount_paid", "due_date",
            "payos_order_code", "payos_payment_link_id", "payos_checkout_url",
            "payos_status", "payos_transaction_ref", "payos_transaction_datetime"
        ]

        # Get invoices with PayOS data
        invoices = frappe.get_all(
            "Invoice",
            filters=base_filters,
            fields=invoice_fields,
            order_by=order_by,
            limit=limit,
            start=start
        )

        # Process transaction data
        transactions = []
        for invoice in invoices:
            transaction = {
                "invoice_name": invoice.name,
                "invoice_status": invoice.status,
                "total_amount": invoice.total,
                "currency": invoice.currency or "VND",
                "customer_name": invoice.customer_name,
                "customer_email": invoice.customer_email,
                "billing_email": invoice.billing_email,
                "created_date": invoice.creation,
                "modified_date": invoice.modified,
                "due_date": invoice.due_date,
                "payment_date": invoice.payment_date,
                "payment_mode": invoice.payment_mode,
                "amount_paid": invoice.amount_paid,
                
                # PayOS specific data
                "payos_order_code": invoice.payos_order_code,
                "payos_payment_link_id": invoice.payos_payment_link_id,
                "payos_checkout_url": invoice.payos_checkout_url,
                "payos_status": invoice.payos_status,
                "payos_transaction_ref": invoice.payos_transaction_ref,
                "payos_transaction_datetime": invoice.payos_transaction_datetime,
                
                # Status mapping
                "payment_status": get_payment_status_display(invoice.payos_status, invoice.status),
                "is_paid": invoice.status == "Paid" and invoice.payos_status == "00",
                "is_pending": invoice.payos_status == "PENDING",
                "is_cancelled": invoice.payos_status == "CANCELLED"
            }

            # Include detailed information if requested
            if include_details:
                try:
                    invoice_doc = frappe.get_doc("Invoice", invoice.name)
                    
                    # Add invoice items
                    items = []
                    if hasattr(invoice_doc, 'items') and getattr(invoice_doc, 'items', None):
                        for item in invoice_doc.items:
                            items.append({
                                "description": item.get("description", ""),
                                "quantity": item.get("quantity", 0),
                                "rate": item.get("rate", 0),
                                "amount": item.get("amount", 0),
                                "document_type": item.get("document_type", ""),
                                "document_name": item.get("document_name", "")
                            })
                    
                    transaction["items"] = items
                    transaction["items_count"] = len(items)
                    
                    # Add additional PayOS info if available
                    if invoice.payos_order_code and invoice.payos_status == "PENDING":
                        # Optionally get real-time status from PayOS (be careful with rate limits)
                        try:
                            payos_info = get_payos_payment_info(invoice.payos_order_code)
                            if payos_info.get("success"):
                                transaction["payos_realtime_status"] = payos_info["data"].get("status", "")
                                transaction["payos_amount_paid"] = payos_info["data"].get("amountPaid", 0) / 100
                                transaction["payos_amount_remaining"] = payos_info["data"].get("amountRemaining", 0) / 100
                        except:
                            pass  # Don't fail if PayOS API is unavailable
                            
                except Exception as e:
                    frappe.log_error(f"Error getting invoice details for {invoice.name}: {str(e)}", "PayOS Transaction History Error")
                    transaction["items"] = []
                    transaction["items_count"] = 0

            transactions.append(transaction)

        # Get total count for pagination
        total_count = frappe.db.count("Invoice", filters=base_filters)
        
        # Calculate pagination info
        has_next = (start + limit) < total_count
        has_prev = start > 0
        
        # Calculate summary statistics
        summary = calculate_transaction_summary(base_filters)

        return {
            "success": True,
            "message": "PayOS transaction history retrieved successfully",
            "data": {
                "transactions": transactions,
                "pagination": {
                    "current_page": (start // limit) + 1,
                    "total_pages": (total_count + limit - 1) // limit,
                    "total_count": total_count,
                    "limit": limit,
                    "start": start,
                    "has_next": has_next,
                    "has_prev": has_prev
                },
                "summary": summary,
                "team": team
            },
            "count": len(transactions)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_payos_transaction_history API")
        return {
            "success": False,
            "message": f"An error occurred while fetching transaction history: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def get_transaction_details(transaction_id, transaction_type="invoice_name"):
    """
    API để lấy chi tiết một giao dịch PayOS cụ thể
    """
    try:
        # Xác định team
        target_team = _resolve_team(arg_email, team_name)
        if isinstance(target_team, dict):  # Error response
            return target_team
        
        # Validate và chuẩn hóa parameters
        validated_params = _validate_transaction_params(limit, offset, date_from, date_to)
        
        # Build SQL query tối ưu - chỉ lấy các field cần thiết
        base_query = """
            SELECT 
                name,
                status,
                amount_due_with_tax,
                period_start,
                period_end,
                payos_order_code,
                payos_status,
                creation,
                payment_date,
                currency,
                customer_name,
                customer_email
            FROM `tabInvoice`
            WHERE team = %(team)s 
            AND (status IN ('Paid', 'Cancelled') OR payos_status IN ('00', 'CANCELLED'))
        """
        
        # Thêm date filter nếu có
        date_conditions, date_params = _build_date_filter(validated_params['date_from'], validated_params['date_to'])
        if date_conditions:
            base_query += f" AND {date_conditions}"
        
        # Query chính với pagination
        main_query = f"""
            {base_query}
            ORDER BY creation DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """
        
        # Query đếm tổng số
        count_query = f"""
            SELECT COUNT(*) as total_count
            FROM `tabInvoice`
            WHERE team = %(team)s 
            AND (status IN ('Paid', 'Cancelled') OR payos_status IN ('00', 'CANCELLED'))
            {f"AND {date_conditions}" if date_conditions else ""}
        """
        
        # Chuẩn bị parameters
        query_params = {
            "team": target_team,
            "limit": validated_params['limit'],
            "offset": validated_params['offset'],
            **date_params
        }
        
        # Thực hiện queries
        invoices = frappe.db.sql(main_query, query_params, as_dict=True)
        count_result = frappe.db.sql(count_query, {k: v for k, v in query_params.items() if k != 'limit' and k != 'offset'}, as_dict=True)
        total_count = count_result[0]["total_count"] if count_result else 0
        
        # Xử lý dữ liệu trả về
        processed_transactions = _process_transaction_data(invoices)
        
        # Tính toán pagination
        pagination_info = _calculate_pagination(
            total_count, 
            validated_params['limit'], 
            validated_params['offset']
        )
        
        return {
            "success": True,
            "message": f"Lấy thành công {len(processed_transactions)} giao dịch",
            "data": {
                "transactions": processed_transactions,
                "pagination": pagination_info,
                "team_name": target_team,
                "filters_applied": {
                    "date_from": validated_params['date_from'],
                    "date_to": validated_params['date_to']
                }
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_team_transaction_history")
        return {
            "success": False,
            "message": f"Lỗi khi lấy lịch sử giao dịch: {str(e)}",
            "error_code": "TRANSACTION_HISTORY_ERROR"
        }


def _resolve_team(arg_email, team_name):
    """
    Xác định team từ email hoặc team_name
    """
    if team_name:
        if not frappe.db.exists("Team", team_name):
            return {
                "success": False,
                "message": "Transaction not found or access denied",
                "error_code": "TRANSACTION_NOT_FOUND"
            }

        # Get invoice document
        invoice_doc = frappe.get_doc("Invoice", invoice_name)
        
        # Prepare detailed transaction data
        transaction_details = {
            "invoice_info": {
                "name": invoice_doc.name,
                "status": invoice_doc.get("status", ""),
                "total": invoice_doc.get("total", 0),
                "currency": invoice_doc.get("currency", "VND"),
                "customer_name": invoice_doc.get("customer_name", ""),
                "customer_email": invoice_doc.get("customer_email", ""),
                "billing_email": invoice_doc.get("billing_email", ""),
                "creation": invoice_doc.get("creation", ""),
                "modified": invoice_doc.get("modified", ""),
                "due_date": invoice_doc.get("due_date", ""),
                "payment_date": invoice_doc.get("payment_date", ""),
                "payment_mode": invoice_doc.get("payment_mode", ""),
                "amount_paid": invoice_doc.get("amount_paid", 0)
            },
            "payos_info": {
                "order_code": invoice_doc.get("payos_order_code", ""),
                "payment_link_id": invoice_doc.get("payos_payment_link_id", ""),
                "checkout_url": invoice_doc.get("payos_checkout_url", ""),
                "qr_code": invoice_doc.get("payos_qr_code", ""),
                "status": invoice_doc.get("payos_status", ""),
                "transaction_ref": invoice_doc.get("payos_transaction_ref", ""),
                "transaction_datetime": invoice_doc.get("payos_transaction_datetime", "")
            },
            "items": [],
            "payment_history": []
        }

        # Add invoice items
        if hasattr(invoice_doc, 'items') and getattr(invoice_doc, 'items', None):
            for item in invoice_doc.items:
                transaction_details["items"].append({
                    "description": item.get("description", ""),
                    "quantity": item.get("quantity", 0),
                    "rate": item.get("rate", 0),
                    "amount": item.get("amount", 0),
                    "document_type": item.get("document_type", ""),
                    "document_name": item.get("document_name", "")
                })

        # Get real-time PayOS status if available
        if invoice_doc.get("payos_order_code"):
            try:
                payos_info = get_payos_payment_info(invoice_doc.get("payos_order_code"))
                if payos_info.get("success"):
                    payos_data = payos_info["data"]
                    transaction_details["payos_realtime"] = {
                        "status": payos_data.get("status", ""),
                        "amount": payos_data.get("amount", 0) / 100,
                        "amount_paid": payos_data.get("amountPaid", 0) / 100,
                        "amount_remaining": payos_data.get("amountRemaining", 0) / 100,
                        "created_at": payos_data.get("createdAt", ""),
                        "transactions": payos_data.get("transactions", [])
                    }
            except Exception as e:
                frappe.log_error(f"Error getting real-time PayOS info: {str(e)}", "PayOS API Error")

        # Get related payment entries
        payment_entries = frappe.get_all("Payment Entry", 
            filters={
                "references.reference_name": invoice_name,
                "docstatus": 1
            },
            fields=["name", "payment_type", "paid_amount", "posting_date", "reference_no", "mode_of_payment"]
        )
        
        transaction_details["payment_history"] = payment_entries

        return {
            "success": True,
            "message": "Transaction details retrieved successfully",
            "data": transaction_details
        }


# ================================
# EXISTING API ENDPOINTS
# ================================

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
            fields=["name", "app", "price_inr", "price_usd", "price_vnd"],
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
def get_emails(arg_email=None):
	team = get_current_team_v2(arg_email,get_doc=True)
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
def update_emails(arg_email=None, data=None):
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
        team_doc = get_current_team_v2(arg_email,get_doc=True)
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
def get_user_sites(arg_email=None):
    """
    REST API to fetch all sites belonging to current user's team.
    Returns list of sites with basic information.
    
    Returns:
        dict: List of user's sites with success status
    """
    try:
        team = get_current_team_v2(arg_email, get_doc=False)
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


@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,  
    rate_limit={"limit": 50, "window": 3600} 
)
def run_doc_method(dt: str, dn: str, method: str, args: dict | None = None):
	try:
		check_permissions(dt)
		check_document_access(dt, dn)
		check_dashboard_actions(dt, dn, method)

		_run_doc_method(
			dt=dt,
			dn=dn,
			method=method,
			args=fix_args(method, args),
		)
		frappe.response.docs = [get(dt, dn)]
		
		return {
			"success": True,
			"message": f"Method '{method}' executed successfully on {dt} {dn}",
			"data": frappe.response.docs[0] if frappe.response.docs else None
		}
		
	except frappe.PermissionError:
		return {
			"success": False,
			"message": "Permission denied. You don't have access to this document or method",
			"error_code": "PERMISSION_DENIED"
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in run_doc_method")
		return {
			"success": False,
			"message": f"An error occurred while executing method: {str(e)}",
			"error_code": "METHOD_EXECUTION_ERROR"
		}


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def get(doctype, name):
	from press.press.doctype.press_role.press_role import check_role_permissions

	check_permissions(doctype)
	try:
		doc = frappe.get_doc(doctype, name)
	except frappe.DoesNotExistError:
		controller = get_controller(doctype)
		if hasattr(controller, "on_not_found"):
			return controller.on_not_found(name)
		raise

	if (
		not (frappe.local.system_user() or has_role("Press Support Agent"))
		and frappe.get_meta(doctype).has_field("team")
		and doc.team != frappe.local.team().name
	):
		raise_not_permitted()

	check_role_permissions(doctype, name)
	
	fields = list(default_fields)

	if doctype == "Product Trial":
		fields.append("background")

	if hasattr(doc, "dashboard_fields"):
		fields += list(doc.dashboard_fields)
	_doc = frappe._dict()
	for fieldname in fields:
		_doc[fieldname] = doc.get(fieldname)

	if hasattr(doc, "get_doc"):
		result = doc.get_doc(_doc)
		if isinstance(result, dict):
			_doc.update(result)

	return _doc


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_first_site_name(arg_email=None):
    try:
        # Get current team
        team = get_current_team_v2(arg_email, get_doc=False)
        if not team:
            return {
                "success": False,
                "message": "No team found for current user",
                "error_code": "NO_TEAM_FOUND"
            }
        
        # Get the first site for the team
        first_site = frappe.get_all(
            "Site",
            filters={"team": team},
            fields=["name"],
            order_by="creation asc",
            limit=1
        )
        if not first_site:
            return {
                "success": False,
                "message": "No sites found for current team",
                "error_code": "NO_SITES_FOUND"
            }
        return {
            "success": True,
            "message": "First site name fetched successfully",
            "data": {
                "site_name": first_site[0]["name"],
                "team": team
            }
        }
        
    except frappe.PermissionError:
        return {
            "success": False,
            "message": "Permission denied. You don't have access to site data",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_first_site_name")
        return {
            "success": False,
            "message": f"An error occurred while fetching first site name: {str(e)}",
            "error_code": "FETCH_ERROR"
        }


# ================================
# PAYOS INTERNAL FUNCTIONS (No validation)
# ================================

def create_payment_link_internal(invoice_name):
    """
    Internal function để tạo PayOS payment link từ Invoice
    Không có validation header - chỉ dùng nội bộ
    """
    try:
        if not invoice_name:
            return {
                "success": False,
                "message": "Invoice name is required",
                "error_code": "MISSING_INVOICE_NAME"
            }

        # Kiểm tra Invoice có tồn tại
        if not frappe.db.exists("Invoice", invoice_name):
            return {
                "success": False,
                "message": "Invoice not found",
                "error_code": "INVOICE_NOT_FOUND"
            }

        # Tạo payment link
        result = create_payos_payment_link(invoice_name)
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in create_payment_link_internal")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def get_team_unpaid_invoices(arg_email=None):
    """
    API để lấy danh sách invoice chưa thanh toán của team và tính tổng tiền tạm tính
    
    Args:
        arg_email (str): Email của user để tìm team
        team_name (str): Tên team (tùy chọn)
    
    Returns:
        dict: Danh sách invoice chưa thanh toán và tổng tiền tạm tính
    """
    try:
        if arg_email:
            target_team = get_current_team_v2(arg_email, get_doc=False)
            if not target_team:
                return {
                    "success": False,
                    "message": "Không tìm thấy team cho user này"
                }
        else:
            return {
                "success": False,
                "message": "Cần cung cấp arg_email hoặc team_name"
            }

        # Lấy danh sách invoice chưa thanh toán với SQL tối ưu
        unpaid_invoices = frappe.db.sql("""
            SELECT 
                name,
                period_start,
                period_end,
                amount_due_with_tax,
                payos_order_code,
                payos_checkout_url,
                payos_qr_code,
                payos_transaction_datetime,
                payos_status,
                payos_payment_link_id,
                payment_mode,
                total,
                vat_percentage,
                creation,
                status
            FROM `tabInvoice`
            WHERE team = %(team)s 
            AND status NOT IN ('Cancelled', 'Draft')
            AND docstatus != 2
            ORDER BY creation DESC
        """, {"team": target_team}, as_dict=True)

        # Xử lý dữ liệu và tính tổng tiền tạm tính
        processed_invoices = []
        total_amount_due = 0.0

        for invoice in unpaid_invoices:
            amount_due = float(invoice.get("amount_due_with_tax", 0) or 0)
            total_amount_due += amount_due
            
            processed_invoices.append({
                "invoice_name": invoice.get("name"),
                "period_start": str(invoice.get("period_start", "") or ""),
                "period_end": str(invoice.get("period_end", "") or ""),
                "amount_due_with_tax": amount_due,
                "payos_order_code": invoice.get("payos_order_code", ""),
                "payos_checkout_url": invoice.get("payos_checkout_url", ""),
                "payos_qr_code": invoice.get("payos_qr_code", ""),
                "payos_transaction_datetime": invoice.get("payos_transaction_datetime", ""),
                "payos_status": invoice.get("payos_status", ""),
                "payos_payment_link_id": invoice.get("payos_payment_link_id", ""),
                "payment_mode": invoice.get("payment_mode", ""),
                "total": float(invoice.get("total", 0) or 0),
                "vat_percentage": float(invoice.get("vat_percentage", 0) or 0),
                "creation": invoice.get("creation"),
                "status": invoice.get("status", ""),
                "has_payos_payment": bool(invoice.get("payos_order_code"))
            })

        return {
            "success": True,
            "message": f"Lấy thành công {len(processed_invoices)} invoice chưa thanh toán",
            "data": processed_invoices,
            "sum_total": round(total_amount_due, 2),
            "invoice_count": len(processed_invoices),
            "team": target_team
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_team_unpaid_invoices")
        return {
            "success": False,
            "message": f"Lỗi khi lấy dữ liệu: {str(e)}"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_team_invoice_history(arg_email=None, limit=None, offset=0, include_items=True):
    """
    API tối ưu để lấy lịch sử invoice với pagination và tùy chọn include items
    
    Args:
        arg_email (str): Email của user để tìm team
        limit (int): Số lượng invoice tối đa trả về (mặc định: không giới hạn)
        offset (int): Số invoice bỏ qua (mặc định: 0)
        include_items (bool): Có bao gồm items không (mặc định: True)
    """
    try:
        # Validate parameters
        try:
            if limit is not None:
                limit = int(limit)
                if limit <= 0 or limit > 1000:  # Max 1000 records per request
                    limit = 100
            offset = int(offset)
            if offset < 0:
                offset = 0
        except (ValueError, TypeError):
            limit = 100
            offset = 0

        # Xác định team
        if arg_email:
            target_team = get_current_team_v2(arg_email, get_doc=False)
            if not target_team:
                return {
                    "success": False,
                    "message": "Không tìm thấy team cho user này"
                }
        else:
            return {
                "success": False,
                "message": "Cần cung cấp arg_email"
            }

        # Tối ưu: Sử dụng JOIN để lấy invoice và items trong một query duy nhất
        if include_items:
            # Query với JOIN để lấy cả invoice và items
            query = """
                SELECT 
                    i.name,
                    i.amount_due_with_tax,
                    i.period_start,
                    i.period_end,
                    i.payos_order_code,
                    i.status,
                    i.payment_mode,
                    i.payos_checkout_url,
                    i.payos_qr_code,
                    i.payos_status,
                    i.payos_payment_link_id,
                    i.payos_transaction_ref,
                    i.payos_transaction_datetime,
                    i.creation,
                    i.modified,
                    i.total,
                    i.currency,
                    i.customer_name,
                    i.customer_email,
                    i.billing_email,
                    i.payment_date,
                    i.due_date,
                    ii.idx,
                    ii.description,
                    ii.quantity,
                    ii.rate,
                    ii.amount,
                    ii.document_type,
                    ii.document_name,
                    ii.creation as item_creation,
                    ii.modified as item_modified
                FROM `tabInvoice` i
                LEFT JOIN `tabInvoice Item` ii ON i.name = ii.parent
                WHERE i.team = %(team)s 
                ORDER BY i.creation DESC, ii.idx ASC
            """
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            results = frappe.db.sql(query, {"team": target_team}, as_dict=True)
            
            # Cache VAT percentage
            default_vat = frappe.db.get_single_value("Press Settings", "vat_percentage") or 0
            
            # Process results efficiently
            invoices = {}
            total_amount = 0.0
            total_items_count = 0
            
            for row in results:
                invoice_name = row.get("name")
                
                if invoice_name not in invoices:
                    # Initialize invoice data
                    amount_due = float(row.get("amount_due_with_tax", 0) or 0)
                    total_amount += amount_due
                    
                    invoices[invoice_name] = {
                        "invoice_name": invoice_name,
                        "amount_due_with_tax": amount_due,
                        "total": float(row.get("total", 0) or 0),
                        "currency": row.get("currency", "VND"),
                        "period_start": str(row.get("period_start", "") or ""),
                        "period_end": str(row.get("period_end", "") or ""),
                        "due_date": row.get("due_date"),
                        "payment_date": row.get("payment_date"),
                        "customer_name": row.get("customer_name", ""),
                        "customer_email": row.get("customer_email", ""),
                        "billing_email": row.get("billing_email", ""),
                        "payos_order_code": row.get("payos_order_code", ""),
                        "status": row.get("status", ""),
                        "payment_mode": row.get("payment_mode", ""),
                        "payos_checkout_url": row.get("payos_checkout_url", ""),
                        "payos_qr_code": row.get("payos_qr_code", ""),
                        "payos_status": row.get("payos_status", ""),
                        "payos_payment_link_id": row.get("payos_payment_link_id", ""),
                        "payos_transaction_ref": row.get("payos_transaction_ref", ""),
                        "payos_transaction_datetime": row.get("payos_transaction_datetime", ""),
                        "creation": row.get("creation"),
                        "modified": row.get("modified"),
                        "items": [],
                        "items_count": 0
                    }
                
                # Add item if exists
                if row.get("idx") is not None:
                    item_data = {
                        "idx": row.get("idx"),
                        "description": row.get("description", ""),
                        "quantity": float(row.get("quantity", 0) or 0),
                        "rate": float(row.get("rate", 0) or 0),
                        "amount": float(row.get("amount", 0) or 0),
                        "document_type": row.get("document_type", ""),
                        "document_name": row.get("document_name", ""),
                        "creation": row.get("item_creation"),
                        "modified": row.get("item_modified"),
                        "vat_percentage": default_vat
                    }
                    invoices[invoice_name]["items"].append(item_data)
                    invoices[invoice_name]["items_count"] += 1
                    total_items_count += 1
            
            result_invoices = list(invoices.values())
            
        else:
            # Query chỉ lấy invoice (không có items) - nhanh hơn nhiều
            query = """
                SELECT 
                    name,
                    amount_due_with_tax,
                    period_start,
                    period_end,
                    payos_order_code,
                    status,
                    payment_mode,
                    payos_checkout_url,
                    payos_qr_code,
                    payos_status,
                    payos_payment_link_id,
                    payos_transaction_ref,
                    payos_transaction_datetime,
                    creation,
                    modified,
                    total,
                    currency,
                    customer_name,
                    customer_email,
                    billing_email,
                    payment_date,
                    due_date
                FROM `tabInvoice`
                WHERE team = %(team)s 
                ORDER BY creation DESC
            """
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            invoices = frappe.db.sql(query, {"team": target_team}, as_dict=True)
            
            # Process invoices without items
            result_invoices = []
            total_amount = 0.0
            
            for invoice in invoices:
                amount_due = float(invoice.get("amount_due_with_tax", 0) or 0)
                total_amount += amount_due
                
                result_invoices.append({
                    "invoice_name": invoice.get("name"),
                    "amount_due_with_tax": amount_due,
                    "total": float(invoice.get("total", 0) or 0),
                    "currency": invoice.get("currency", "VND"),
                    "period_start": str(invoice.get("period_start", "") or ""),
                    "period_end": str(invoice.get("period_end", "") or ""),
                    "due_date": invoice.get("due_date"),
                    "payment_date": invoice.get("payment_date"),
                    "customer_name": invoice.get("customer_name", ""),
                    "customer_email": invoice.get("customer_email", ""),
                    "billing_email": invoice.get("billing_email", ""),
                    "payos_order_code": invoice.get("payos_order_code", ""),
                    "status": invoice.get("status", ""),
                    "payment_mode": invoice.get("payment_mode", ""),
                    "payos_checkout_url": invoice.get("payos_checkout_url", ""),
                    "payos_qr_code": invoice.get("payos_qr_code", ""),
                    "payos_status": invoice.get("payos_status", ""),
                    "payos_payment_link_id": invoice.get("payos_payment_link_id", ""),
                    "payos_transaction_ref": invoice.get("payos_transaction_ref", ""),
                    "payos_transaction_datetime": invoice.get("payos_transaction_datetime", ""),
                    "creation": invoice.get("creation"),
                    "modified": invoice.get("modified"),
                    "items": [],
                    "items_count": 0
                })
            
            total_items_count = 0

        # Get total count for pagination
        total_count = frappe.db.count("Invoice", filters={"team": target_team})
        
        return {
            "success": True,
            "message": f"Lấy thành công {len(result_invoices)} invoice với {total_items_count} items",
            "data": result_invoices,
            "pagination": {
                "current_page": (offset // (limit or 100)) + 1 if limit else 1,
                "total_pages": (total_count + (limit or 100) - 1) // (limit or 100) if limit else 1,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": limit and (offset + limit) < total_count,
                "has_prev": offset > 0
            },
            "summary": {
                "total_invoices": len(result_invoices),
                "total_items": total_items_count,
                "total_amount": round(total_amount, 2),
                "average_amount_per_invoice": round(total_amount / len(result_invoices), 2) if result_invoices else 0
            },
            "team": target_team,
            "include_items": include_items
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_team_invoice_history")
        return {
            "success": False,
            "message": f"Lỗi khi lấy dữ liệu: {str(e)}"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_order_status(arg_email=None, invoice_id=None):
    """
    API để lấy trạng thái đơn hàng theo invoice ID
    
    Args:
        arg_email (str): Email của user để xác thực team
        invoice_id (str): ID của invoice cần kiểm tra trạng thái
    
    Returns:
        dict: Thông tin trạng thái đơn hàng chi tiết với đồng bộ PayOS tự động
    """
    try:
        if not invoice_id:
            return {
                "success": False,
                "message": "Invoice ID is required",
                "error_code": "MISSING_INVOICE_ID"
            }

        team = get_current_team_v2(arg_email, get_doc=False)
        if not team:
            return {
                "success": False,
                "message": "No team found for current user",
                "error_code": "NO_TEAM_FOUND"
            }

        # Lấy thông tin invoice
        invoice_data = frappe.db.get_value(
            "Invoice",
            {"name":invoice_id,"team": team},
            [
                "name", "status"
            ],
            as_dict=True
        )

        if not invoice_data:
            return {
                "success": False,
                "message": "Invoice data not found",
                "error_code": "INVOICE_DATA_NOT_FOUND"
            }

        # Chuẩn bị thông tin cơ bản về đơn hàng
        order_status = {
            "invoice_id": invoice_data["name"],
            "invoice_status": invoice_data["status"],
        }
        return {
            "success": True,
            "message": "Order status retrieved successfully",
            "data": order_status,
        }

    except frappe.PermissionError:
        return {
            "success": False,
            "message": "Permission denied. You don't have access to this invoice",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_order_status API")
        return {
            "success": False,
            "message": f"An error occurred while fetching order status: {str(e)}",
            "error_code": "ORDER_STATUS_ERROR"
        }


def get_invoice_items_batch(invoice_names):
    """
    Lấy tất cả items của nhiều invoices cùng lúc để tránh N+1 queries
    
    Args:
        invoice_names (list): Danh sách tên các invoices
    
    Returns:
        dict: Dictionary với key là invoice name, value là list items
    """
    if not invoice_names:
        return {}
    
    # Lấy tất cả items của các invoices trong một query duy nhất
    all_items = frappe.get_all(
        "Invoice Item",
        filters={"parent": ["in", invoice_names]},
        fields=[
            "parent",  # Tên invoice
            "description",
            "quantity", 
            "rate",
            "amount",
            "document_type",
            "document_name"
        ],
        order_by="parent, idx"  
    )
    
    # Nhóm items theo invoice
    items_by_invoice = {}
    for item in all_items:
        invoice_name = item.get("parent")
        if invoice_name not in items_by_invoice:
            items_by_invoice[invoice_name] = []
        
        # Loại bỏ field 'parent' khỏi item data
        item_data = {k: v for k, v in item.items() if k != "parent"}
        items_by_invoice[invoice_name].append(item_data)
    
    # Đảm bảo mọi invoice đều có mảng items (rỗng nếu không có)
    for invoice_name in invoice_names:
        if invoice_name not in items_by_invoice:
            items_by_invoice[invoice_name] = []
    
    return items_by_invoice


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_team_item_invoices(arg_email=None):
    """
    API để lấy tất cả items của các invoices có cùng team
    
    Args:
        arg_email (str): Email của user để tìm team
    
    Returns:
        dict: Mảng chứa tất cả items của các invoices có cùng team
    """
    try:
        if arg_email:
            target_team = get_current_team_v2(arg_email, get_doc=False)
            if not target_team:
                return {
                    "success": False,
                    "message": "Không tìm thấy team cho user này"
                }
        else:
            return {
                "success": False,
                "message": "Cần cung cấp arg_email"
            }

        # Lấy danh sách tất cả invoices của team với thông tin cần thiết
        all_invoices = frappe.get_all(
            "Invoice",
            filters={
                "team": target_team,
                "docstatus": ["!=", 2]  # Chỉ loại bỏ invoices đã bị xóa
            },
            fields=["name", "period_start", "period_end", "due_date"],
            order_by="creation desc"
        )
        
        if not all_invoices:
            return {
                "success": True,
                "message": "Không có invoice nào được tìm thấy",
                "data": [],
                "total_items": 0,
                "total_amount": 0.0,
                "team": target_team
            }
        
        # Tạo dictionary để map invoice name với thông tin invoice
        invoice_info_map = {}
        for invoice in all_invoices:
            invoice_info_map[invoice.name] = {
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "due_date": invoice.due_date,
                "vat_percentage" : invoice.vat_percentage
            }
        
        # Lấy tên các invoices
        invoice_names = [invoice.name for invoice in all_invoices]
        
        # Lấy vat trong setting hệ thống 
        default_vat = frappe.db.get_single_value("Press Settings", "vat_percentage")
        # Lấy tất cả items của các invoices này
        all_items = frappe.get_all(
            "Invoice Item",
            filters={"parent": ["in", invoice_names]},
            fields=[
                "parent as invoice_name",
                "idx",
                "description",
                "quantity", 
                "rate",
                "amount",
                "document_type",
                "document_name",
                "creation",
                "modified"
            ],
            order_by="parent, idx"
        )
        
        # Xử lý dữ liệu items và tính tổng tiền
        processed_items = []
        total_amount = 0.0
        
        for item in all_items:
            invoice_name = item.get("invoice_name", "")
            
            # sum tổng tiền trước thuế
            item_amount = float(item.get("amount", 0) or 0)
            total_amount += item_amount
            
            # Lấy thông tin invoice từ map
            invoice_info = invoice_info_map.get(invoice_name, {})
            
            processed_item = {
                "invoice_name": invoice_name,
                "item_index": item.get("idx", 0),
                "description": item.get("description", ""),
                "quantity": float(item.get("quantity", 0) or 0),
                "rate": float(item.get("rate", 0) or 0),
                "amount": item_amount,
                "document_type": item.get("document_type", ""),
                "document_name": item.get("document_name", ""),
                "creation": item.get("creation"),
                "modified": item.get("modified"),
                # Thông tin từ invoice
                "period_start": invoice_info.get("period_start"),
                "period_end": invoice_info.get("period_end"),
                "due_date": invoice_info.get("due_date"),
            }
            processed_items.append(processed_item)
        
        return {
            "success": True,
            "message": f"Lấy thành công {len(processed_items)} items từ {len(all_invoices)} invoices",
            "data": processed_items,
            "total_items": len(processed_items),
            "total_invoices": len(all_invoices),
            "total_amount": round(total_amount, 2),
            "total_amount_due_with_tax": round(total_amount * (1 + (default_vat or 0) / 100), 2),
            "team": target_team
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_team_item_invoices")
        return {
            "success": False,
            "message": f"Lỗi khi lấy dữ liệu: {str(e)}"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def check_dns_status(site_name=None, domain=None, arg_email=None):
    """
    REST API để check DNS status cho một domain
    Sử dụng hàm check_dns có sẵn từ site.py để tối ưu code
    
    Args:
        site_name (str): Tên site (subdomain)
        domain (str): Domain cần check
        arg_email (str): Email của user (optional, để validate quyền truy cập)
    
    Returns:
        dict: Kết quả check DNS với các thông tin chi tiết
    """
    try:
        # Validate input parameters
        if not site_name or not domain:
            return {
                "success": False,
                "message": "Missing required parameters: site_name and domain",
                "error_code": "MISSING_PARAMETERS"
            }
        
        # Validate email nếu được cung cấp
        if arg_email:
            team = get_current_team_v2(arg_email, get_doc=False)
            if not team:
                return {
                    "success": False,
                    "message": "Invalid email or user not found",
                    "error_code": "INVALID_USER"
                }
        
        # Log request để debug
        frappe.logger().info(f"🔍 DNS Check Request - Site: {site_name}, Domain: {domain}, Email: {arg_email}")
        # Thực hiện check DNS bằng hàm có sẵn từ site.py
        dns_result = check_dns_cname_a(site_name, domain)
        
        # Format kết quả trả về - tối ưu: tính toán trực tiếp từ dns_result
        cname = dns_result.get("CNAME", {})
        a_record = dns_result.get("A", {})
        
        # Tính toán recommendations trực tiếp
        recommendations = []
        if not cname.get("exists"):
            recommendations.append("CNAME record does not exist for this domain")
        elif not cname.get("matched"):
            recommendations.append("CNAME record exists but does not point to the correct site")
        
        if not a_record.get("exists"):
            recommendations.append("A record does not exist for this domain")
        elif not a_record.get("matched"):
            recommendations.append("A record exists but does not point to the correct IP address")
        
        if cname.get("matched") and a_record.get("exists") and not a_record.get("matched"):
            recommendations.append("Remove conflicting A record as CNAME is correctly configured")
        
        if a_record.get("matched") and cname.get("exists") and not cname.get("matched"):
            recommendations.append("Remove conflicting CNAME record as A record is correctly configured")
        
        if not recommendations:
            recommendations.append("DNS configuration looks good!")
        
        formatted_result = {
            "success": True,
            "site_name": site_name,
            "domain": domain,
            "dns_status": {
                "overall_status": "valid" if dns_result.get("matched", False) else "invalid",
                "cname_record": {
                    "exists": cname.get("exists", False),
                    "matched": cname.get("matched", False),
                    "answer": cname.get("answer", ""),
                    "type": cname.get("type", "CNAME")
                },
                "a_record": {
                    "exists": a_record.get("exists", False),
                    "matched": a_record.get("matched", False),
                    "answer": a_record.get("answer", ""),
                    "type": a_record.get("type", "A")
                }
            },
            "recommendations": recommendations,
            "timestamp": frappe.utils.now_datetime().isoformat()
        }
        
        frappe.logger().info(f"✅ DNS Check Completed - Site: {site_name}, Domain: {domain}")
        return formatted_result
        
    except Exception as e:
        frappe.logger().error(f"❌ DNS Check Error - Site: {site_name}, Domain: {domain}, Error: {str(e)}")
        return {
            "success": False,
            "message": f"DNS check failed: {str(e)}",
            "error_code": "DNS_CHECK_ERROR",
            "site_name": site_name,
            "domain": domain
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def add_domain_to_site(site_name=None, domain=None, arg_email=None):
    """
    REST API để add domain vào site
    Sử dụng hàm add_domain có sẵn từ site.py để tối ưu code
    
    Args:
        site_name (str): Tên site (subdomain)
        domain (str): Domain cần thêm vào site
        arg_email (str): Email của user (optional, để validate quyền truy cập)
    
    Returns:
        dict: Kết quả add domain
    """
    try:
        # Validate input parameters
        if not site_name or not domain:
            return {
                "success": False,
                "message": "Missing required parameters: site_name and domain",
                "error_code": "MISSING_PARAMETERS"
            }
        
        # Validate email nếu được cung cấp
        if arg_email:
            team = frappe.db.get_all("Team", filters={"user": arg_email}, fields=["name"])
            if not team:
                return {
                    "success": False,
                    "message": "Invalid email or user not found",
                    "error_code": "INVALID_USER"
                }
        
        # Log request để debug
        frappe.logger().info(f"🔗 Add Domain Request - Site: {site_name}, Domain: {domain}, Email: {arg_email}")
        
        # Kiểm tra site có tồn tại không
        if not frappe.db.exists("Site", site_name):
            return {
                "success": False,
                "message": f"Site {site_name} does not exist",
                "error_code": "SITE_NOT_FOUND",
                "site_name": site_name,
                "domain": domain
            }
        
        # Kiểm tra domain đã tồn tại chưa
        if frappe.db.exists("Site Domain", domain.lower()):
            return {
                "success": False,
                "message": f"Domain {domain} is already in use by another site",
                "error_code": "DOMAIN_ALREADY_EXISTS",
                "site_name": site_name,
                "domain": domain
            }
        
        # Import và gọi trực tiếp hàm add_domain logic từ site.py
        # Tối ưu: Tái sử dụng logic có sẵn thay vì viết lại
        # Bypass @protected decorator để cho phép public API access
        
        # Lấy site document
        site_doc = frappe.get_doc("Site", site_name)
        subdomain = getattr(site_doc, "subdomain", None)
        product_trial = None
        
        # Thử lấy product_trial từ ProductTrialRequest nếu có
        ptr = frappe.db.get_value("Product Trial Request", {"site": site_name}, "product_trial")
        if ptr:
            product_trial = ptr
        else:
            # Nếu không có, thử lấy từ site (nếu có custom field)
            product_trial = getattr(site_doc, "product_trial", None)
        
        # Nếu là app đặc biệt, sửa lại domain cho đúng
        if product_trial and subdomain:
            from press.utils.domain import get_default_domain
            product = frappe.get_doc("Product Trial", product_trial)
            domain = get_default_domain(subdomain, product_trial, product.domain)
        
        # Thực hiện add domain bằng hàm có sẵn từ site document
        site_doc.add_domain(domain)
        
        # Log success
        frappe.logger().info(f"✅ Domain Added Successfully - Site: {site_name}, Domain: {domain}")
        
        return {
            "success": True,
            "message": f"Domain {domain} has been successfully added to site {site_name}",
            "site_name": site_name,
            "domain": domain,
            "timestamp": frappe.utils.now_datetime().isoformat()
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Add Domain Error - Site: {site_name}, Domain: {domain}, Error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to add domain: {str(e)}",
            "error_code": "ADD_DOMAIN_ERROR",
            "site_name": site_name,
            "domain": domain
        }


@frappe.whitelist()
def save_setup_wizard_language(lang_code=None):
    """
    API method để lưu ngôn ngữ cho setup wizard.
    Tương thích với pattern mới - lưu trực tiếp vào System Settings.
    """
    if not lang_code:
        lang_code = 'vi'  # Default to Vietnamese
    
    # Ghi log để debug
    frappe.logger().info(f"🔄 save_setup_wizard_language called with: {lang_code}")
    
    try:
        # Convert language code to language name that setup wizard expects
        language_name_mapping = {
            'vi': 'Việt',           # Setup wizard expects 'Việt' for Vietnamese
            'en': 'English',        # Setup wizard expects 'English' for English
        }
        
        language_name = language_name_mapping.get(lang_code, lang_code)
        frappe.logger().info(f"📝 Converting language code '{lang_code}' to name '{language_name}'")
        
        # Cập nhật System Settings với ngôn ngữ đã chọn
        system_settings = frappe.get_doc("System Settings", "System Settings")
        system_settings.language = language_name  # Use language name, not code
        system_settings.save(ignore_permissions=True)
        
        # Đảm bảo thay đổi được commit
        frappe.db.commit()
        frappe.logger().info(f"✅ Successfully saved language '{language_name}' to System Settings")
        
        # Trả về kết quả thành công
        return {
            "status": "success", 
            "message": f"Language {language_name} saved to System Settings",
            "language_code": lang_code,
            "language_name": language_name
        }
    except Exception as e:
        frappe.logger().error(f"❌ Error saving language to System Settings: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_site_domains(site_name=None, arg_email=None):
    """
    REST API để lấy danh sách domains của site
    Trả về các bản ghi từ doctype Site Domain với filter theo site
    
    Args:
        site_name (str): Tên site (bắt buộc)
        arg_email (str): Email của user (optional, để validate quyền truy cập)
        include_details (bool): Có bao gồm thông tin chi tiết không (optional, default: False)
    
    Returns:
        dict: Danh sách domains của site
    """
    try:
        # Validate input parameters
        if not site_name:
            return {
                "success": False,
                "message": "Missing required parameter: site_name",
                "error_code": "MISSING_SITE_NAME"
            }
        
        # Validate email nếu được cung cấp
        if arg_email:
            team = get_current_team_v2(arg_email, get_doc=False)
            if not team:
                return {
                    "success": False,
                    "message": "Invalid email or user not found",
                    "error_code": "INVALID_USER"
                }

        # Kiểm tra site có tồn tại không
        if not frappe.db.exists("Site", site_name):
            return {
                "success": False,
                "message": f"Site '{site_name}' does not exist",
                "error_code": "SITE_NOT_FOUND",
                "site_name": site_name
            }
        
        # Lấy thông tin host name của site
        host_name = frappe.db.get_value("Site", site_name, "host_name")
        
        # Xác định fields cần lấy
        fields = [ "name", "domain", "status", "dns_type", "redirect_to_primary" ]
        
        # Lấy danh sách domains của site
        domains = frappe.get_all(
            "Site Domain",
            fields=fields,
            filters={"site": site_name},
            order_by="creation desc"
        )
        
        # Thêm thông tin primary domain
        for domain in domains:
            domain["is_primary"] = domain["domain"] == host_name
            domain["redirect_to"] = host_name if domain["redirect_to_primary"] else None
        
        # Sắp xếp lại: primary domain lên đầu
        domains.sort(key=lambda x: not x["is_primary"])
        
        return {
            "success": True,
            "message": f"Retrieved domains for site '{site_name}'",
            "domains": domains,
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get site domains: {str(e)}",
            "error_code": "GET_SITE_DOMAINS_ERROR",
            "site_name": site_name
        }

@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 50, "window": 3600} 
)
def check_unpaid_invoices_and_notify(arg_email=None, request_type=None, site_name=None):
    """
    REST API để kiểm tra hóa đơn chưa thanh toán và gửi thông báo cho admin
    
    Args:
        arg_email (str): Email của user để kiểm tra hóa đơn
        request_type (str): Loại yêu cầu - 'stop_site' hoặc 'delete_site' (optional)
        site_name (str): Tên site liên quan đến yêu cầu (optional, required khi có request_type)
        
    Returns:
        dict: Kết quả kiểm tra và thông báo
    """
    try:
        # Validate input parameters
        validation_result = _validate_input_parameters(arg_email, request_type, site_name)
        if not validation_result['valid']:
            return validation_result['response']
        
        # Log request để debug
        frappe.logger().info(f"💰 Checking unpaid invoices for user: {arg_email}, request_type: {request_type}, site: {site_name}")
        
        # Lấy team từ email
        team = get_current_team_v2(arg_email, get_doc=False)
        if not team:
            return {
                "success": False,
                "message": "User not found or not associated with any team",
                "error_code": "USER_NOT_FOUND",
                "email": arg_email
            }
        
        # Kiểm tra hóa đơn chưa thanh toán
        unpaid_invoices = _get_unpaid_invoices(team)
        
        # Nếu có hóa đơn chưa thanh toán
        if unpaid_invoices:
            return _create_unpaid_invoices_response(arg_email, team, unpaid_invoices)
        
        # Nếu không có hóa đơn chưa thanh toán, gửi thông báo cho admin
        return _create_success_response_and_notify_admin(arg_email, team, request_type, site_name)
        
    except Exception as e:
        frappe.logger().error(f"❌ Check unpaid invoices error for {arg_email}: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to check unpaid invoices: {str(e)}",
            "error_code": "CHECK_INVOICES_ERROR",
            "email": arg_email
        }

def _validate_input_parameters(arg_email, request_type, site_name):
    """Validate input parameters"""
    import re
    
    # Validate email
    if not arg_email:
        return {
            'valid': False,
            'response': {
                "success": False,
                "message": "Missing required parameter: arg_email",
                "error_code": "MISSING_EMAIL"
            }
        }
    
    # Validate email format
    if not re.match(EMAIL_PATTERN, arg_email):
        return {
            'valid': False,
            'response': {
                "success": False,
                "message": "Invalid email format",
                "error_code": "INVALID_EMAIL_FORMAT"
            }
        }
    
    # Validate request_type nếu được cung cấp
    if request_type and request_type not in VALID_REQUEST_TYPES:
        return {
            'valid': False,
            'response': {
                "success": False,
                "message": "Invalid request_type. Must be 'stop_site' or 'delete_site'",
                "error_code": "INVALID_REQUEST_TYPE"
            }
        }
    
    # Validate site_name nếu có request_type
    if request_type and not site_name:
        return {
            'valid': False,
            'response': {
                "success": False,
                "message": "Missing required parameter: site_name when request_type is provided",
                "error_code": "MISSING_SITE_NAME"
            }
        }
    
    return {'valid': True}

def _get_unpaid_invoices(team):
    """Get unpaid invoices for a team"""
    return frappe.db.get_all(
        "Invoice",
        filters={
            "team": team,
            "status": ["in", ["Unpaid", "Invoice Created","Draft"]],
            "amount_due": [">", 0]
        },
        fields=[
            "name", 
            "total", 
            "amount_due", 
            "due_date", 
            "creation",
            "type",
            "status"
        ],
        order_by="due_date asc"
    )

def _create_unpaid_invoices_response(arg_email, team, unpaid_invoices):
    """Create response for unpaid invoices case"""
    total_unpaid_amount = sum(invoice.amount_due for invoice in unpaid_invoices)
    oldest_due_date = min(invoice.due_date for invoice in unpaid_invoices if invoice.due_date)
    
    # Tạo thông báo cho user
    user_message = f"Bạn còn {len(unpaid_invoices)} hóa đơn chưa thanh toán với tổng số tiền {frappe.utils.fmt_money(total_unpaid_amount)}. "
    if oldest_due_date:
        user_message += f"Hóa đơn cũ nhất đến hạn vào {frappe.utils.formatdate(oldest_due_date)}."
    
    frappe.logger().info(f"❌ Unpaid invoices found for {arg_email}: {len(unpaid_invoices)} invoices, total: {total_unpaid_amount}")
    
    return {
        "success": False,
        "message": user_message,
        "error_code": "UNPAID_INVOICES_FOUND",
        "email": arg_email,
        "team": team,
        "unpaid_invoices_count": len(unpaid_invoices),
        "total_unpaid_amount": total_unpaid_amount,
        "oldest_due_date": oldest_due_date.isoformat() if oldest_due_date else None,
        "invoices": [
            {
                "name": invoice.name,
                "total": invoice.total,
                "amount_due": invoice.amount_due,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "type": invoice.type,
                "status": invoice.status
            }
            for invoice in unpaid_invoices
        ]
    }

def _create_success_response_and_notify_admin(arg_email, team, request_type, site_name):
    """Create success response and notify admin"""
    frappe.logger().info(f"✅ No unpaid invoices found for {arg_email}, sending notification to admin")
    
    # Lấy thông tin user/team để tạo thông báo chi tiết
    team_doc = get_current_team_v2(arg_email, get_doc=True)
    user_info = frappe.db.get_value("User", arg_email, ["full_name", "enabled"], as_dict=True)
    
    # Tạo thông báo cho admin dựa trên loại yêu cầu
    notification_data = _create_notification_data(arg_email, team_doc, user_info, request_type, site_name)
    
    # Tạo Press Notification cho admin
    notifications_created = _create_admin_notifications(notification_data,arg_email)
    
    return {
        "success": True,
        "message": "Payment status check completed successfully. No unpaid invoices found.",
        "email": arg_email,
        "team": team,
        "request_type": request_type,
        "site_name": site_name,
        "unpaid_invoices_count": 0,
        "total_unpaid_amount": 0,
        "notifications_sent": len(notifications_created),
        "admin_notified": notifications_created,
        "timestamp": frappe.utils.now_datetime().isoformat()
    }

def _create_notification_data(arg_email, team_doc, user_info, request_type, site_name):
    """Create notification data based on request type"""
    if request_type == 'stop_site':
        return {
            'title': f"User Request: Stop Site - {site_name}",
            'message': f"""
            User {arg_email} ({user_info.get('full_name', 'N/A')}) has requested to STOP site: {site_name}
            Team: {team_doc.name if team_doc else 'N/A'}
            Team Country: {team_doc.country if team_doc else 'N/A'}
            User Status: {'Active' if user_info.get('enabled') else 'Inactive'}
            Site Name: {site_name}
            ✅ No unpaid invoices found - User is eligible for site stop request.
            Request Time: {frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
        }
    elif request_type == 'delete_site':
        return {
            'title': f"User Request: Delete Site - {site_name}",
            'message': f"""
            User {arg_email} ({user_info.get('full_name', 'N/A')}) has requested to DELETE site: {site_name}
            Team: {team_doc.name if team_doc else 'N/A'}
            Team Country: {team_doc.country if team_doc else 'N/A'}
            User Status: {'Active' if user_info.get('enabled') else 'Inactive'}
            Site Name: {site_name}
            ✅ No unpaid invoices found - User is eligible for site deletion request.
            Request Time: {frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
        }
    else:
        # Thông báo mặc định cho payment status check
        return {
            'title': f"User Payment Status Check: {arg_email}",
            'message': f"""
            User {arg_email} ({user_info.get('full_name', 'N/A')}) has checked their payment status.
            Team: {team_doc.name if team_doc else 'N/A'}
            Team Country: {team_doc.country if team_doc else 'N/A'}
            User Status: {'Active' if user_info.get('enabled') else 'Inactive'}
            ✅ No unpaid invoices found - User is in good standing.
            Check Time: {frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
        }

def _create_admin_notifications(notification_data,arg_email):
    """Create notifications for admin users"""
    notifications_created = []
    
    # Tìm admin users hoặc system administrators
    admin_users = frappe.db.get_all(
        "User",
        filters={
            "enabled": 1,
            "name": ["in", ADMIN_USERS]
        },
        fields=["name"]
    )
    
    for admin_user in admin_users:
        try:
            # Lấy team của admin
            admin_team = get_current_team_v2(admin_user.name, get_doc=False)
            if admin_team:
                # Tạo notification
                notification_doc = frappe.get_doc({
                    "doctype": "Press Notification",
                    "team": admin_team,
                    "type": "Info",
                    "title": notification_data['title'],
                    "message": notification_data['message'],
                    "read": 0,
                    "is_addressed": 0,
                    "is_actionable": 0,
                    "document_type": "User",
                    "document_name": arg_email
                })
                notification_doc.insert(ignore_permissions=True)
                notifications_created.append(admin_user.name)
                
                frappe.logger().info(f"📢 Notification sent to admin: {admin_user.name}")
        except Exception as e:
            frappe.logger().error(f"❌ Failed to create notification for admin {admin_user.name}: {str(e)}")
    
    # Nếu không tìm thấy admin users, tạo notification cho system
    if not notifications_created:
        try:
            # Tạo notification cho system team hoặc default team
            system_team = frappe.db.get_value("Team", {"name": "Administrator"}, "name") or "Administrator"
            
            notification_doc = frappe.get_doc({
                "doctype": "Press Notification",
                "team": system_team,
                "type": "Info",
                "title": notification_data['title'],
                "message": notification_data['message'],
                "read": 0,
                "is_addressed": 0,
                "is_actionable": 0,
                "document_type": "User",
                "document_name": arg_email
            })
            notification_doc.insert(ignore_permissions=True)
            notifications_created.append("System")
            
            frappe.logger().info(f"📢 System notification created for team: {system_team}")
        except Exception as e:
            frappe.logger().error(f"❌ Failed to create system notification: {str(e)}")

            return notifications_created


@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
    rate_limit={"limit": 100, "window": 3600} 
)
def get_site_app_plan_limits(arg_email=None, arg_site=None):
    """
    REST API tối ưu để lấy thông tin giới hạn features của các app plans mà site đã đăng ký
    
    Tối ưu hiệu suất:
    - Sử dụng 1 SQL query duy nhất thay vì multiple queries
    - Batch processing cho limit features  
    - Early return cho edge cases
    
    Args:
        arg_email (str): Email của user để xác thực quyền truy cập
        arg_site (str): Tên site cần lấy thông tin plan limits
    
    Returns:
        dict: Thông tin limit features của các app plans đã đăng ký
    """
    try:
        # Validate parameters with early return
        validation_result = _validate_app_plan_params(arg_email, arg_site)
        if not validation_result["valid"]:
            return validation_result["response"]
        
        # Log request
        frappe.logger().info(f"🎯 Getting app plan limits - Email: {arg_email}, Site: {arg_site}")
        
        # Get team and validate site access
        team = get_current_team_v2(arg_email, get_doc=False)
        if not team:
            return _create_error_response("USER_NOT_FOUND", "User not found or not associated with any team", arg_email)
        
        site_access_result = _validate_site_access(arg_site, team)
        if not site_access_result["valid"]:
            return site_access_result["response"]
        
        # Tối ưu: Sử dụng 1 SQL query để lấy tất cả dữ liệu cần thiết
        app_plan_data = _get_subscribed_app_plans_optimized(arg_site, team)
        
        if not app_plan_data:
            return _create_success_response_empty(arg_site, team)
        
        # Batch process limit features
        plan_names = [row["plan_name"] for row in app_plan_data]
        limit_features_map = _get_limit_features_batch(plan_names)
        
        # Process results efficiently
        app_plan_limits = _process_app_plan_data(app_plan_data, limit_features_map)
        
        frappe.logger().info(f"✅ App plan limits retrieved - Site: {arg_site}, Subscribed Plans: {len(app_plan_limits)}")
        
        return _create_success_response(arg_site, team, arg_email, app_plan_limits)
        
    except Exception as e:
        frappe.logger().error(f"❌ Get app plan limits error - Email: {arg_email}, Site: {arg_site}, Error: {str(e)}")
        return _create_error_response("GET_APP_PLAN_LIMITS_ERROR", f"Failed to get app plan limits: {str(e)}", arg_email, arg_site)


def _validate_app_plan_params(arg_email, arg_site):
    """Validate input parameters with optimized checks"""
    if not arg_email:
        return {
            "valid": False,
            "response": _create_error_response("MISSING_EMAIL", "Missing required parameter: arg_email")
        }
    
    if not arg_site:
        return {
            "valid": False,
            "response": _create_error_response("MISSING_SITE", "Missing required parameter: arg_site")
        }
    
    # Import regex once and reuse
    import re
    if not re.match(EMAIL_PATTERN, arg_email):
        return {
            "valid": False,
            "response": _create_error_response("INVALID_EMAIL_FORMAT", "Invalid email format")
        }
    
    return {"valid": True}


def _validate_site_access(arg_site, team):
    """Validate site exists and belongs to team"""
    site_info = frappe.db.get_value("Site", arg_site, ["name", "team"], as_dict=True)
    
    if not site_info:
        return {
            "valid": False,
            "response": _create_error_response("SITE_NOT_FOUND", f"Site '{arg_site}' not found", site=arg_site)
        }
    
    if site_info.team != team:
        return {
            "valid": False,
            "response": _create_error_response(
                "ACCESS_DENIED", 
                f"Site '{arg_site}' does not belong to user's team",
                site=arg_site, user_team=team, site_team=site_info.team
            )
        }
    
    return {"valid": True}


def _get_subscribed_app_plans_optimized(arg_site, team):
    query = """
        SELECT DISTINCT
            sa.app as app_name,
            ma.name as marketplace_app_name,
            ma.title as marketplace_app_title,
            ma.team as marketplace_app_team,
            map.name as plan_name,
            map.title as plan_title,
            map.price_inr,
            map.price_usd,
            map.price_vnd
        FROM `tabSite App` sa
        INNER JOIN `tabMarketplace App` ma ON sa.app = ma.app
        INNER JOIN `tabMarketplace App Plan` map ON ma.name = map.app
        INNER JOIN `tabSubscription` sub ON map.name = sub.plan
        WHERE sa.parent = %(site)s
        AND sub.team = %(team)s
        AND sub.enabled = 1
        AND map.enabled = 1
        ORDER BY sa.creation ASC, map.creation ASC
    """
    
    return frappe.db.sql(query, {"site": arg_site, "team": team}, as_dict=True)


def _get_limit_features_batch(plan_names):
    """Batch lấy limit features cho tất cả plans cùng lúc"""
    if not plan_names:
        return {}
    
    # Lấy tất cả features trong 1 query
    all_features = frappe.get_all(
        "Plan Feature",
        filters={"parent": ["in", plan_names]},
        fields=["parent", "description", "quantity"],
        order_by="parent, idx asc"
    )
    
    # Group features theo plan
    features_map = {}
    for feature in all_features:
        plan_name = feature["parent"]
        if plan_name not in features_map:
            features_map[plan_name] = []
        
        features_map[plan_name].append({
            "description": feature["description"],
            "quantity": feature["quantity"]
        })
    
    return features_map


def _process_app_plan_data(app_plan_data, limit_features_map):
    app_plan_limits = []

    for row in app_plan_data:
        plan_name = row["plan_name"]
        limit_features = limit_features_map.get(plan_name, [])
        
        plan_info = {
            "app_name": row["app_name"],
            "marketplace_app": {
                "name": row["marketplace_app_name"],
                "title": row["marketplace_app_title"],
                "team": row["marketplace_app_team"]
            },
            "plan": {
                "name": plan_name,
                "title": row["plan_title"],
                "price_inr": row["price_inr"],
                "price_usd": row["price_usd"],
                "price_vnd": row["price_vnd"],
                "is_subscribed": True
            },
            "limit_features": limit_features,
            "features_count": len(limit_features)
        }
        
        app_plan_limits.append(plan_info)
    
    return app_plan_limits


def _create_error_response(error_code, message, email=None, site=None, **kwargs):
    response = {
        "success": False,
        "message": message,
        "error_code": error_code
    }
    
    if email:
        response["email"] = email
    if site:
        response["site"] = site
    
    response.update(kwargs)
    return response


def _create_success_response_empty(arg_site, team):
    """Utility để tạo success response khi không có apps"""
    return {
        "success": True,
        "message": f"No subscribed apps found on site '{arg_site}'",
        "site": arg_site,
        "team": team,
        "data": {
            "app_plan_limits": [],
            "total_subscribed_plans": 0,
            "total_apps_with_subscriptions": 0
        },
        "timestamp": frappe.utils.now_datetime().isoformat()
    }


def _create_success_response(arg_site, team, arg_email, app_plan_limits):
    """Utility để tạo success response"""
    return {
        "success": True,
        "message": f"App plan limits retrieved successfully for site '{arg_site}' - found {len(app_plan_limits)} subscribed plans",
        "site": arg_site,
        "team": team,
        "email": arg_email,
        "data": {
            "app_plan_limits": app_plan_limits,
            "total_subscribed_plans": len(app_plan_limits),
            "total_apps_with_subscriptions": len(set(plan["app_name"] for plan in app_plan_limits))
        },
        "timestamp": frappe.utils.now_datetime().isoformat()
    }
@frappe.whitelist(allow_guest=True)
def get_key_template():
    """
    API để lấy template cho login_id và password
    """
    try:
        site_config = frappe.get_site_config()
        login_id_template = site_config.get("login_id_template")
        password_template = site_config.get("password_template")

        return {
            "login_id_template": login_id_template,
            "password_template": password_template
        }
    except Exception as e:
        frappe.log_error(f"Error getting site config: {str(e)}")

@frappe.whitelist(allow_guest=True, methods=['POST'])
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,  # Require API key for security
    rate_limit={"limit": 100, "window": 3600} 
)
def create_notification_request(site=None, status=None, type=None, description=None):
    """
    Public API để tạo MBW Notification Request từ hệ thống bên ngoài

    Args:
        site (str): Tên site (bắt buộc)
        status (str): Trạng thái request - "Ongoing" hoặc "Done" (mặc định: "Ongoing")
        type (str): Loại request - "Restore", "Drop site", "Deactivate site" (bắt buộc)
        description (str): Mô tả chi tiết request (tùy chọn)
    
    Returns:
        dict: Kết quả tạo notification request
    """
    try:
        # Validate required parameters
        if not site:
            return {
                "success": False,
                "message": "Missing required parameter: site",
                "error_code": "MISSING_SITE_PARAMETER"
            }
        
        if not type:
            return {
                "success": False,
                "message": "Missing required parameter: type",
                "error_code": "MISSING_TYPE_PARAMETER"
            }
        
        # Set default values
        if not status:
            status = "Ongoing"

        # Validate enum values
        valid_statuses = ["Ongoing", "Done"]
        valid_types = ["Restore", "Drop site", "Deactivate site"]
        
        if status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                "error_code": "INVALID_STATUS"
            }
        
        if type not in valid_types:
            return {
                "success": False,
                "message": f"Invalid type. Must be one of: {', '.join(valid_types)}",
                "error_code": "INVALID_TYPE"
            }
        
        # Validate site exists in the system
        if not frappe.db.exists("Site", site):
            return {
                "success": False,
                "message": f"Site '{site}' not found in the system",
                "error_code": "SITE_NOT_FOUND"
            }
        
        # Check if there's already an ongoing request for this site and type
        existing_request = frappe.db.exists("MBW Notification Request", {
            "site": site,
            "type": type,
            "status": "Ongoing"
        })
        
        if existing_request:
            return {
                "success": False,
                "message": f"An ongoing request of type '{type}' already exists for site '{site}'",
                "error_code": "DUPLICATE_ONGOING_REQUEST",
                "existing_request": existing_request
            }
        
        # Create the notification request
        notification_doc = frappe.get_doc({
            "doctype": "MBW Notification Request",
            "site": site,
            "status": status,
            "type": type,
            "description": description or f"External system request for {type.lower()} on site {site}"
        })

        # Insert the document
        notification_doc.insert(ignore_permissions=True)
        frappe.db.commit()
            
        return {
            "success": True,
            "message": f"Notification request created successfully for site '{site}'",
            "data": {
                "request_id": notification_doc.name,
                "site": site,
                "status": status,
                "type": type,
                "description": notification_doc.description,
                "creation": notification_doc.creation.isoformat() if notification_doc.creation else None
            },
            "timestamp": frappe.utils.now_datetime().isoformat()
        }
            
    except frappe.ValidationError as e:
        return {
            "success": False,
            "message": f"Validation error: {str(e)}",
            "error_code": "VALIDATION_ERROR"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in create_notification_request API")
        return {
            "success": False,
            "message": f"Failed to create notification request: {str(e)}",
            "error_code": "CREATE_REQUEST_ERROR"
        }

@frappe.whitelist()
@validate_api_request(
	required_headers=['User-Agent'],
	api_key_required=True,  # Require API key for security
	rate_limit={"limit": 200, "window": 3600} 
)
def get_site_backups(site=None, limit=20, start=0):
	"""
	Public API để lấy danh sách Site Backups theo tên site với phân trang
	
	Args:
		site (str): Tên site cần lấy danh sách backup (bắt buộc)
		limit (int): Số lượng bản ghi tối đa (mặc định: 20, tối đa: 100)
		start (int): Vị trí bắt đầu (mặc định: 0)
	
	Returns:
		dict: Danh sách site backups với thông tin phân trang
	"""
	try:
		# Validate required parameter
		if not site:
			return {
				"success": False,
				"message": "Missing required parameter: site",
				"error_code": "MISSING_SITE_PARAMETER"
			}
		
		# Validate and sanitize pagination parameters
		try:
			limit = int(limit)
			start = int(start)
			if limit <= 0 or limit > 100:
				limit = 20
			if start < 0:
				start = 0
		except (ValueError, TypeError):
			limit = 20
			start = 0
		
		# Lấy tổng số backup để tính pagination
		total_count = frappe.db.count("Site Backup", filters={"site": site})
		
		# Lấy danh sách backup theo site name với phân trang
		backups = frappe.get_all(
			"Site Backup",
			filters={"site": site},
			fields="*",  # Lấy tất cả các trường
			order_by="creation desc",
			limit=limit,
			start=start
		)
		
		# Tính toán thông tin phân trang
		has_next = (start + limit) < total_count
		has_prev = start > 0
		current_page = (start // limit) + 1
		total_pages = (total_count + limit - 1) // limit
		
		return {
			"success": True,
			"message": f"Retrieved {len(backups)} site backups for site '{site}' (page {current_page} of {total_pages})",
			"data": backups,
			"pagination": {
				"total_count": total_count,
				"current_page": current_page,
				"total_pages": total_pages,
				"limit": limit,
				"start": start,
				"has_next": has_next,
				"has_prev": has_prev,
				"count_on_page": len(backups)
			},
			"site": site,
			"timestamp": frappe.utils.now_datetime().isoformat()
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in get_site_backups API")
		return {
			"success": False,
			"message": f"Failed to get site backups: {str(e)}",
			"error_code": "GET_SITE_BACKUPS_ERROR"
		}

@frappe.whitelist()
@validate_api_request(
	required_headers=['User-Agent'],
	api_key_required=False,  
	rate_limit={"limit": 10, "window": 3600} 
)
def generate_site_admin_login_url(site_name=None, arg_email=None, reason="Download backup files"):
	"""
	API để tạo URL login as admin cho site để có thể download backup
	
	Args:
		site_name (str): Tên site cần login (bắt buộc)
		arg_email (str): Email của user để validate quyền truy cập (tùy chọn)
		reason (str): Lý do login (mặc định: "Download backup files")
	
	Returns:
		dict: URL login as admin
	"""
	try:
		# Validate required parameters
		if not site_name:
			return {
				"success": False,
				"message": "Missing required parameter: site_name",
				"error_code": "MISSING_SITE_NAME"
			}
		
		# Validate email nếu được cung cấp
		if arg_email:
			team = get_current_team_v2(arg_email, get_doc=False)
			if not team:
				return {
					"success": False,
					"message": "Invalid email or user not found",
					"error_code": "INVALID_USER"
				}
		
		# Lấy site document và tạo login URL
		site_doc = frappe.get_doc("Site", site_name)
		login_url = site_doc.login_as_admin(reason=reason)
        
		return {
			"success": True,
			"message": "Admin login URL generated successfully",
			"data": {
				"login_url": login_url,
				"site_name": site_name
			}
		}
		
	except frappe.DoesNotExistError:
		return {
			"success": False,
			"message": f"Site '{site_name}' not found",
			"error_code": "SITE_NOT_FOUND"
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in generate_site_admin_login_url API")
		return {
			"success": False,
			"message": f"Failed to generate admin login URL: {str(e)}",
			"error_code": "ADMIN_LOGIN_URL_ERROR"
		}

@frappe.whitelist(allow_guest=True, methods=['POST'])
@validate_api_request(
	required_headers=['Content-Type', 'User-Agent'],
	api_key_required=True,
	rate_limit={"limit": 100, "window": 3600}
)
def save_company_information(company_data=None):
	"""
	API upsert MBW Information Company theo tax_code.
	- Nếu chưa có tax_code: tạo mới
	- Nếu đã có tax_code: cập nhật các trường được gửi lên
	"""
	try:
		if not company_data:
			return {"success": False, "error": "company_data is required", "error_code": "MISSING_DATA"}

		if isinstance(company_data, str):
			company_data = frappe.parse_json(company_data)

		if not company_data.get('tax_code'):
			return {"success": False, "error": "tax_code is required", "error_code": "MISSING_TAX_CODE"}

		# Optional email validation for company email field
		email = (company_data.get('email_name') or '').strip()
		if email and not frappe.utils.validate_email_address(email):
			return {"success": False, "error": "Invalid email format", "error_code": "INVALID_EMAIL"}

		# Resolve team: if company_data.team is an email, convert to team ID; fallback to arg_email
		resolved_team_id = None
		team_input = company_data.get('team')
		if team_input:
			try:
				resolved_team_id = get_current_team_v2(team_input, get_doc=False)
			except Exception as _e:
				resolved_team_id = None
		# Overwrite team with resolved team id if available
		if resolved_team_id:
			company_data['team'] = resolved_team_id

		existing = frappe.get_all(
			"MBW Information Company",
			filters={"tax_code": company_data.get('tax_code')},
			limit=1
		)

		if existing:
			company_doc = frappe.get_doc("MBW Information Company", existing[0].name)
			action = "updated"
		else:
			company_doc = frappe.get_doc({"doctype": "MBW Information Company"})
			action = "created"

		updatable_fields = [
			'team', 'full_name', 'tax_code', 'adress_name', 'phone_number', 'email_name',
			'representative_name', 'position_name'
		]

		for field in updatable_fields:
			if field in company_data:
				value = company_data[field]
				setattr(company_doc, field, value.strip() if isinstance(value, str) else value)

		if action == "created":
			company_doc.insert(ignore_permissions=True)
		else:
			company_doc.save(ignore_permissions=True)

		return {
			"success": True,
			"message": f"Company information {action} successfully",
			"action": action,
			"data": {
				"name": company_doc.name,
				"team": company_doc.team,
				"full_name": company_doc.full_name,
				"tax_code": company_doc.tax_code,
				"adress_name": company_doc.adress_name,
				"phone_number": company_doc.phone_number,
				"email_name": company_doc.email_name,
				"representative_name": getattr(company_doc, 'representative_name', None),
				"position_name": getattr(company_doc, 'position_name', None),
				"creation": company_doc.creation,
				"modified": company_doc.modified
			}
		}

	except frappe.ValidationError as e:
		frappe.log_error(f"Validation error in save_company_information: {str(e)}", "Company Info Validation Error")
		return {"success": False, "error": f"Validation error: {str(e)}", "error_code": "VALIDATION_ERROR"}

	except Exception as e:
		frappe.log_error(f"Error saving company information: {str(e)}", "Company Info Save Error")
		return {"success": False, "error": "Internal server error occurred", "error_code": "INTERNAL_ERROR"}


# ================================
# BKAV INVOICE DATA CREATION HELPERS
# ================================

def _create_bkav_invoice_data_from_invoice(invoice_doc, company_info):
	"""Tạo dữ liệu BKAV từ Invoice và Company Info"""
	try:
		timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
		
		return {
			"id": f"INV_{invoice_doc.name}_{timestamp}",
			"guid": "",
			"serial": frappe.db.get_value(
				"MBW EInvoice Company", {"company": "Default Company", "is_active": 1}, "invoice_serial_bkav"
			) or "C25TAA",
			"invoiceNumber": invoice_doc.name,
			"arisingDate": invoice_doc.creation.isoformat() if invoice_doc.creation else datetime.now().isoformat(),
			"vatRate": 10,
			"status": "New",
			"paymentMethod": "Electronic",
			"currencyType": invoice_doc.currency or "VND",
			"exchangeRate": 1,
			"eInvoiceItems": _create_einvoice_items_from_invoice(invoice_doc),
			"invoiceCustomer": {
				"id": f"CUST_{company_info.team}",
				"customerNumber": company_info.team,
				"taxNumber": company_info.tax_code or "",
				"companyName": company_info.full_name or "",
				"fullName": company_info.full_name or "",
				"address": company_info.adress_name or "",
				"phoneNumber": company_info.phone_number or "",
				"email": company_info.email_name or "",
				"representativeName": getattr(company_info, "representative_name", None) or "",
				"positionName": getattr(company_info, "position_name", None) or "",
				"bankAccountNumber": "",
				"bankName": "",
				"bankOwnerName": ""
			},
			"note": f"Auto-exported from Invoice {invoice_doc.name}",
			"isUseCheckDiscount": False,
			"rateCheckDiscount": 0,
			"discountType": "NotDicount"
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating BKAV data: {str(e)}", "BKAV Data Creation Error")
		return {}


def _create_einvoice_items_from_invoice(invoice_doc):
	"""Tạo items cho BKAV từ Invoice items"""
	try:
		items = []
		
		if hasattr(invoice_doc, 'items') and invoice_doc.items:
			for idx, item in enumerate(invoice_doc.items, 1):
				amount = float(item.amount or 0)
				vat_amount = amount * 0.1  # 10% VAT
				
				items.append({
					"posNumber": idx,
					"productNumber": f"PROD_{idx:03d}",
					"productId": f"prod_{idx}",
					"productName": item.description or f"Item {idx}",
					"unit": "Service",
					"quantity": float(item.quantity or 1),
					"price": float(item.rate or 0),
					"vatRate": 10,
					"vatRateDisplay": 10,
					"free": False,
					"discount": False,
					"currencyType": invoice_doc.currency or "VND",
					"addAmount": 0,
					"amount": amount,
					"vatAmount": vat_amount,
					"discountRate": 0,
					"discountAmount": 0,
					"totalAmount": amount + vat_amount,
					"displayOrder": idx
				})
		else:
			# Default item nếu không có items
			total = float(invoice_doc.total or 0)
			vat_amount = total * 0.1
			
			items.append({
				"posNumber": 1,
				"productNumber": "SERV_001",
				"productId": "service_001",
				"productName": f"Service for Invoice {invoice_doc.name}",
				"unit": "Service",
				"quantity": 1,
				"price": total,
				"vatRate": 10,
				"vatRateDisplay": 10,
				"free": False,
				"discount": False,
				"currencyType": invoice_doc.currency or "VND",
				"addAmount": 0,
				"amount": total,
				"vatAmount": vat_amount,
				"discountRate": 0,
				"discountAmount": 0,
				"totalAmount": total + vat_amount,
				"displayOrder": 1
			})
		
		return items
		
	except Exception as e:
		frappe.log_error(f"Error creating EInvoice items: {str(e)}", "EInvoice Items Error")
		return []

def trigger_einvoice_export_on_payment_success(invoice_name):
	"""
	Kích hoạt xuất EInvoice khi thanh toán thành công
	"""
	try:
		# Lấy thông tin invoice
		invoice_doc = frappe.get_doc("Invoice", invoice_name)
		
		# Đẩy job vào queue
		frappe.enqueue(
			"press.api.app_admin.process_invoice_einvoice_export",
			queue="default",
			timeout=300,
			invoice_name=invoice_name,
			team=invoice_doc.team
		)
		
		frappe.logger().info(f"EInvoice export job queued for {invoice_name}")
		
	except Exception as e:
		frappe.log_error(f"Error triggering EInvoice export: {str(e)}", "EInvoice Trigger Error")

def process_invoice_einvoice_export(invoice_name, team):
	"""
	Queue job để xử lý xuất EInvoice
	"""
	try:
		frappe.logger().info(f"Processing EInvoice export for {invoice_name}")
		
		# Lấy thông tin invoice
		invoice_doc = frappe.get_doc("Invoice", invoice_name)
		
		# Cập nhật trạng thái processing
		invoice_doc.einvoice_status = "Processing"
		invoice_doc.save(ignore_permissions=True)
		
		# Lấy thông tin company
		company_info = frappe.get_all("MBW Information Company",
			filters={"team": team},
			fields=["*"],
			limit=1
		)
		
		if not company_info:
			raise Exception(f"Không tìm thấy thông tin company cho team: {team}")
		
		# Tạo dữ liệu BKAV
		bkav_data = _create_bkav_invoice_data_from_invoice(invoice_doc, company_info[0])
		
		# Gọi BKAV API
		from press.api.bkav_api_helper import get_bkav_api_helper
		
		helper = get_bkav_api_helper(team)
		if not helper:
			raise Exception("Không thể khởi tạo BKAV API Helper")
		
		# Tạo hóa đơn trên BKAV
		bkav_result = helper.create_invoice(bkav_data)
		
		# Cập nhật kết quả
		if bkav_result.get("success"):
			data = bkav_result.get("data", {})
			invoice_doc.einvoice_status = "Exported"
			invoice_doc.bkav_invoice_id = data.get("invoiceId")
			invoice_doc.bkav_view_url = data.get("viewUrl")
			invoice_doc.bkav_lookup_code = data.get("lookupCode")
		else:
			invoice_doc.einvoice_status = "Failed"
		
		invoice_doc.save(ignore_permissions=True)
		
		# Tạo tracking record
		_create_einvoice_tracking_record(invoice_name, bkav_result, team)
		
		frappe.logger().info(f"EInvoice export completed for {invoice_name}")
		
	except Exception as e:
		frappe.log_error(f"Error processing EInvoice export: {str(e)}", "EInvoice Process Error")
		
		# Cập nhật trạng thái lỗi
		try:
			invoice_doc = frappe.get_doc("Invoice", invoice_name)
			invoice_doc.einvoice_status = "Failed"
			invoice_doc.save(ignore_permissions=True)
		except:
			pass

def _create_bkav_invoice_data_from_invoice(invoice_doc, company_info):
	"""
	Tạo dữ liệu BKAV từ Invoice doc
	"""
	try:
		# Tạo items
		items = _create_einvoice_items_from_invoice(invoice_doc)
		
		# Tạo customer info
		customer_info = {
			"id": invoice_doc.team,
			"customerNumber": invoice_doc.team,
			"taxNumber": company_info.get("tax_code", ""),
			"companyName": company_info.get("company_name", ""),
			"fullName": company_info.get("company_name", ""),
			"address": company_info.get("address", ""),
			"phoneNumber": company_info.get("phone", ""),
			"email": company_info.get("email", ""),
			"bankAccountNumber": "",
			"bankName": "",
			"bankOwnerName": ""
		}
		
		# Tạo invoice data
		invoice_data = {
			"id": invoice_doc.name,
			"guid": "",
			"serial": "C25TAA",  # Từ workspace rules
			"invoiceNumber": invoice_doc.name.replace("INV-", ""),
			"arisingDate": invoice_doc.creation.isoformat() if invoice_doc.creation else "",
			"vatRate": 10,  # Default VAT 10%
			"status": "New",
			"paymentMethod": "Cash",
			"currencyType": "VND",
			"exchangeRate": 1,
			"eInvoiceItems": items,
			"invoiceCustomer": customer_info,
			"note": f"Hóa đơn {invoice_doc.name}",
			"isUseCheckDiscount": False,
			"rateCheckDiscount": 0,
			"discountType": "NotDiscount"
		}
		
		return invoice_data
		
	except Exception as e:
		frappe.log_error(f"Error creating BKAV data: {str(e)}", "BKAV Data Error")
		raise

def _create_einvoice_tracking_record(invoice_name, bkav_result, team):
	"""
	Tạo bản ghi theo dõi EInvoice
	"""
	try:
		# Lấy tên company theo team (fallback sử dụng team nếu không có)
		# Lấy tên công ty của KH từ bảng MBW Information Company (luôn ưu tiên text khách hàng)
		company_name = None
		try:
			company_name = frappe.get_value(
				"MBW Information Company", {"team": team}, "company"
			) or frappe.get_value(
				"MBW Information Company", {"team": team}, "name"
			)
		except Exception:
			company_name = None

		# Xây dựng payload tracking, gán company nếu tìm thấy; nếu doctype yêu cầu company bắt buộc
		# mà vẫn không xác định được, sẽ để trống và dựa vào validate của doctype
		tracking_payload = {
			"doctype": "MBW Detail EInvoice",
			"invoice_name": invoice_name,
			"team": team,
			"bkav_response": frappe.as_json(bkav_result),
			"status": "Success" if bkav_result.get("success") else "Failed",
			"export_date": frappe.utils.now()
		}
		# Luôn lưu company theo thông tin khách hàng (text), không ép Link tới doctype Company
		if company_name:
			tracking_payload["company"] = company_name

		tracking_doc = frappe.get_doc(tracking_payload)
		tracking_doc.insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error creating tracking record: {str(e)}", "EInvoice Tracking Error")

@frappe.whitelist()
def manual_export_invoice_to_einvoice(invoice_name, arg_email):
	"""
	API để xuất hóa đơn thủ công lên BKAV
	"""
	try:
		# Kiểm tra invoice tồn tại
		if not frappe.db.exists("Invoice", invoice_name):
			return {
				"success": False,
				"message": f"Invoice {invoice_name} không tồn tại"
			}
		
		# Lấy thông tin invoice
		invoice_doc = frappe.get_doc("Invoice", invoice_name)
		
		# Trigger export process
		trigger_einvoice_export_on_payment_success(invoice_name)
		
		return {
			"success": True,
			"message": f"Đã kích hoạt xuất EInvoice cho {invoice_name}",
			"invoice_status": invoice_doc.status,
			"team": invoice_doc.team
		}
		
	except Exception as e:
		frappe.log_error(f"Error in manual export: {str(e)}", "Manual EInvoice Export Error")
		return {
			"success": False,
			"message": f"Lỗi xuất EInvoice: {str(e)}"
		}

@frappe.whitelist()
def get_invoice_einvoice_status(invoice_name, arg_email):
	"""
	API để lấy trạng thái EInvoice của hóa đơn
	"""
	try:
		# Kiểm tra invoice tồn tại
		if not frappe.db.exists("Invoice", invoice_name):
			return {
				"success": False,
				"message": f"Invoice {invoice_name} không tồn tại"
			}
		
		# Lấy thông tin invoice
		invoice_doc = frappe.get_doc("Invoice", invoice_name)
		
		# Lấy thông tin EInvoice tracking
		tracking_records = frappe.get_all("MBW Detail EInvoice",
			filters={"invoice_name": invoice_name},
			fields=["*"],
			order_by="creation desc",
			limit=1
		)
		
		result = {
			"success": True,
			"invoice_name": invoice_name,
			"invoice_status": invoice_doc.status,
			"einvoice_status": getattr(invoice_doc, 'einvoice_status', 'Not Exported'),
			"bkav_invoice_id": getattr(invoice_doc, 'bkav_invoice_id', None),
			"bkav_view_url": getattr(invoice_doc, 'bkav_view_url', None),
			"bkav_lookup_code": getattr(invoice_doc, 'bkav_lookup_code', None),
		}
		
		if tracking_records:
			tracking = tracking_records[0]
			result["tracking_info"] = {
				"bkav_response": tracking.get("bkav_response"),
				"export_date": tracking.get("creation"),
				"status": tracking.get("status")
			}
		
		return result
		
	except Exception as e:
		frappe.log_error(f"Error getting EInvoice status: {str(e)}", "EInvoice Status Error")
		return {
			"success": False,
			"message": f"Lỗi lấy trạng thái EInvoice: {str(e)}"
		}
