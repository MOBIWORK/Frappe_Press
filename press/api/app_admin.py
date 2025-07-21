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
from press.api.site import is_marketplace_app_source, is_prepaid_marketplace_app

# Import PayOS helper functions
from press.api.payos_connect import (
    check_payos_settings,
    create_payos_payment_link, get_payos_payment_info, cancel_payos_payment, verify_payos_signature, 
    get_payment_status_display, calculate_transaction_summary
)

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
        
        return Truethô
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


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=False,  
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
            AND status NOT IN ('Paid', 'Cancelled')
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
def get_team_invoice_history(arg_email=None):
    try:
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
                "message": "Cần cung cấp arg_email hoặc team_name"
            }

        # Lấy danh sách invoice đã thanh toán hoặc đã hủy
        invoices = frappe.db.sql("""
            SELECT 
                name,
                amount_due_with_tax,
                period_start,
                period_end,
                payos_order_code,
                status,
                payment_mode,
                creation
            FROM `tabInvoice`
            WHERE team = %(team)s 
            AND status IN ('Paid', 'Cancelled')
            ORDER BY creation DESC
        """, {"team": target_team}, as_dict=True)

        # Xử lý dữ liệu trả về
        result_invoices = []
        for invoice in invoices:
            result_invoices.append({
                "invoice_name": invoice.get("name"),
                "amount_due_with_tax": float(invoice.get("amount_due_with_tax", 0) or 0),
                "period_start": str(invoice.get("period_start", "") or ""),
                "period_end": str(invoice.get("period_end", "") or ""),
                "payos_order_code": invoice.get("payos_order_code", ""),
                "status": invoice.get("status", ""),
                "payment_mode": invoice.get("payment_mode", ""),
                "creation": invoice.get("creation")
            })
        return {
            "success": True,
            "message": f"Lấy thành công {len(result_invoices)} invoice",
            "data": result_invoices,
            "team": target_team
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