import frappe
import json
import requests
import pytz
import hmac
import hashlib
import time
from datetime import datetime, timedelta

# PayOS Base URL
PAYOS_BASE_URL = "https://api-merchant.payos.vn"

def check_payos_settings():
    # Required fields for PayOS integration
    required_fields = ["payos_client_id", "payos_api_key", "payos_checksum_key", "payos_webhook_url_current"]
    # Optional fields (can be empty)
    optional_fields = ["payos_return_url", "payos_cancel_url"]
    
    try:
        payos_settings = frappe.get_doc("Press Settings", "Press Settings")
    except frappe.DoesNotExistError:
        return None

    if not payos_settings:
        return None

    settings_dict = {}
    
    # Check required fields
    for field in required_fields:
        value = payos_settings.get(field)
        if not value:
            return None
        settings_dict[field] = value
    
    # Add optional fields (even if empty)
    for field in optional_fields:
        value = payos_settings.get(field) or ""
        settings_dict[field] = value

    return settings_dict


# def get_current_team_v2(get_doc=False):
#     if frappe.session.user == "Guest":
#         frappe.throw("Not Permitted", frappe.PermissionError)

#     if not hasattr(frappe.local, "request"):
#         # if this is not a request, send the current user as default team
#         # always use parent_team for background jobs
#         team_filters = {"user": frappe.session.user, "enabled": 1, "parent_team": ("is", "not set")}
#         if get_doc:
#             try:
#                 team_name = frappe.get_value("Team", team_filters, "name")
#                 if team_name and isinstance(team_name, str):
#                     return frappe.get_doc("Team", team_name)
#                 else:
#                     frappe.throw("No team found for user", frappe.PermissionError)
#             except frappe.DoesNotExistError:
#                 frappe.throw("No team found for user", frappe.PermissionError)
#         else:
#             return frappe.get_value("Team", team_filters, "name")

#     user_is_system_user = getattr(frappe.session.data, 'user_type', None) == "System User"
#     # get team passed via request header
#     team = frappe.get_request_header("X-Press-Team")
#     user_is_press_admin = frappe.db.exists(
#         "Has Role", {"parent": frappe.session.user, "role": "Press Admin"}
#     )

#     if (
#         not team
#         and user_is_press_admin
#         and frappe.db.exists("Team", {"user": frappe.session.user})
#     ):
#         # if user has_role of Press Admin then just return current user as default team
#         team_filters = {"user": frappe.session.user, "enabled": 1}
#         if get_doc:
#             team_name = frappe.get_value("Team", team_filters, "name")
#             if team_name and isinstance(team_name, str):
#                 return frappe.get_doc("Team", team_name)
#             else:
#                 frappe.throw("No team found for user", frappe.PermissionError)
#         else:
#             return frappe.get_value("Team", team_filters, "name")

#     if not team:
#         # if team is not passed via header, get the first team that this user is part of
#         team_list = frappe.db.sql(
#             """select t.name from `tabTeam` t
#             inner join `tabTeam Member` tm on tm.parent = t.name
#             where tm.user = %s and tm.parenttype = 'Team' and t.enabled = 1
#             order by t.creation asc
#             limit 1""",
#             (frappe.session.user,),
#             as_dict=True,
#         )
#         if team_list and len(team_list) > 0:
#             team = team_list[0]["name"]
#         else:
#             frappe.throw("No team found for user", frappe.PermissionError)

#     if not frappe.db.exists("Team", team):
#         frappe.throw("Invalid Team", frappe.PermissionError)

#     valid_team = frappe.db.exists(
#         "Team Member", {"parenttype": "Team",
#                         "parent": team, "user": frappe.session.user}
#     )
#     if not valid_team and not user_is_system_user:
#         frappe.throw(
#             "User {0} does not belong to Team {1}".format(
#                 frappe.session.user, team),
#             frappe.PermissionError,
#         )

#     if get_doc and isinstance(team, str):
#         return frappe.get_doc("Team", team)

#     return team


def generate_payos_signature(data_dict, checksum_key):
    """
    Tạo signature cho PayOS sử dụng HMAC SHA256
    Data được sắp xếp theo alphabet
    """
    try:
        
        # Loại bỏ các field empty hoặc None
        filtered_data = {k: v for k, v in data_dict.items() if v != "" and v is not None}
        
        # Sắp xếp data theo alphabet
        sorted_data = sorted(filtered_data.items())
        
        # Tạo query string theo format PayOS: key=value&key=value
        query_string = "&".join([f"{key}={value}" for key, value in sorted_data])

        if len(query_string) > 100:
            # Log query string đã cắt bớt
            short_query = query_string[:100] + "..."
            frappe.log_error(f"PayOS query (truncated): {short_query}", "PayOS Signature")
            
            # Log chi tiết vào message thay vì title
            frappe.log_error(f"Full PayOS signature query string:\n{query_string}", "PayOS Signature Detail")
        else:
            frappe.log_error(f"PayOS query: {query_string}", "PayOS Signature")
        
        # Tạo signature sử dụng HMAC SHA256
        signature = hmac.new(
            checksum_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # ✅ SỬA LỖI: Log signature ngắn gọn
        frappe.log_error(f"PayOS signature: {signature[:16]}...", "PayOS Signature")
        
        return signature
    except Exception as e:
        # ✅ SỬA LỖI: Log error ngắn gọn
        frappe.log_error(f"PayOS signature error: {str(e)[:100]}", "PayOS Error")
        return None


def verify_payos_signature(data_dict, received_signature, checksum_key):
    """
    Xác minh signature từ PayOS
    """
    try:
        # ✅ SỬA LỖI: Tối ưu logging để tránh lỗi 140 ký tự
        frappe.log_error(f"PayOS verify data: {str(data_dict)[:80]}...", "PayOS Verify")
        frappe.log_error(f"PayOS received sig: {received_signature[:16]}...", "PayOS Verify")
        frappe.log_error(f"PayOS key length: {len(checksum_key)}", "PayOS Verify")
        
        calculated_signature = generate_payos_signature(data_dict, checksum_key)
        
        frappe.log_error(f"PayOS calc sig: {calculated_signature[:16]}...", "PayOS Verify")
        frappe.log_error(f"PayOS match: {calculated_signature == received_signature}", "PayOS Verify")
        
        return calculated_signature == received_signature
    except Exception as e:
        # ✅ SỬA LỖI: Log error ngắn gọn
        frappe.log_error(f"PayOS verify error: {str(e)[:100]}", "PayOS Error")
        return False


def create_payos_payment_link(invoice_name):
    """
    Tạo link thanh toán PayOS từ Invoice
    """
    try:
        # Lấy thông tin PayOS settings
        payos_settings = check_payos_settings()
        if not payos_settings:
            return {
                "success": False,
                "message": "PayOS settings not configured",
                "error_code": "PAYOS_SETTINGS_MISSING"
            }

        # Lấy thông tin Invoice
        invoice_doc = frappe.get_doc("Invoice", invoice_name)
        
        # KIỂM TRA NẾU ĐÃ CÓ PAYOS ORDER CODE
        if invoice_doc.get('payos_order_code'):
            print(f"⚠️ Invoice {invoice_name} đã có PayOS order code: {invoice_doc.get('payos_order_code')}")
            return {
                "success": False,
                "message": "PayOS payment link already exists for this invoice",
                "error_code": "PAYOS_LINK_EXISTS",
                "data": {
                    "order_code": invoice_doc.get('payos_order_code'),
                    "checkout_url": invoice_doc.get('payos_checkout_url', ''),
                    "qr_code": invoice_doc.get('payos_qr_code', ''),
                    "status": invoice_doc.get('payos_status', '')
                }
            }
        
        # Tạo order code duy nhất (sử dụng timestamp + invoice name hash)
        order_code = int(time.time() * 1000) % 2147483647  # Đảm bảo không vượt quá int32
        
        # KIỂM TRA DUPLICATE ORDER CODE TRONG DATABASE
        existing_invoice = frappe.db.get_value("Invoice", {"payos_order_code": order_code}, "name")
        if existing_invoice:
            # Nếu trùng, tạo order code mới
            import random
            order_code = int(time.time() * 1000 + random.randint(1, 999)) % 2147483647
            print(f"🔄 Tạo order code mới do trùng lặp: {order_code}")
        
        # KHỞI TẠO VAT_PERCENTAGE NGAY TẠI ĐÂY
        vat_percentage = float(invoice_doc.get('vat_percentage', 0) or 0)
        
        # KIỂM TRA CURRENCY ĐỂ XỬ LÝ ĐÚNG CÁCH
        currency = invoice_doc.get('currency', 'VND')
        
        # TÍNH TOÁN SỐ TIỀN BAO GỒM VAT - LÀM TRÒN NGAY TẠI ĐÂY
        # Sử dụng amount_due_with_tax nếu có, ngược lại dùng total
        final_amount = 0
        if hasattr(invoice_doc, 'amount_due_with_tax') and invoice_doc.get('amount_due_with_tax'):
            # LÀM TRÒN VÀ BỎ PHẦN THẬP PHÂN
            final_amount = round(float(invoice_doc.get('amount_due_with_tax', 0) or 0))
            print(f"💰 Sử dụng amount_due_with_tax (làm tròn): {final_amount:,.0f} {currency}")
        else:
            # Fallback: tính VAT thủ công nếu chưa có amount_due_with_tax
            base_amount = round(float(invoice_doc.get('total', 0) or 0))
            
            if vat_percentage > 0:
                vat_amount = round(base_amount * (vat_percentage / 100))
                final_amount = base_amount + vat_amount
                print(f"💰 Tính VAT thủ công (làm tròn): {base_amount:,.0f} + VAT {vat_percentage}% = {final_amount:,.0f} {currency}")
            else:
                final_amount = base_amount
                print(f"💰 Không có VAT (làm tròn): {final_amount:,.0f} {currency}")
        
        # Chuẩn bị dữ liệu items từ invoice với tên sản phẩm và số lượng chính xác
        items = []
        if hasattr(invoice_doc, 'items') and getattr(invoice_doc, 'items', None):
            for item in invoice_doc.items:
                # LẤY TÊN SẢN PHẨM CHÍNH XÁC
                item_name = "Unknown Service"
                
                # Ưu tiên lấy tên từ document_name (tên app)
                if item.get("document_name"):
                    document_name = str(item.get("document_name", ""))
                    # Nếu là app, lấy title từ Marketplace App
                    if item.get("document_type") == "Marketplace App":
                        app_title = frappe.db.get_value("Marketplace App", document_name, "title")
                        if app_title:
                            item_name = f"App: {app_title}"
                        else:
                            item_name = f"App: {document_name}"
                    # Nếu là Site, lấy tên site
                    elif item.get("document_type") == "Site":
                        site_name = document_name.split(".archived")[0]  # Remove .archived suffix
                        item_name = f"Site: {site_name}"
                    # Nếu là Server
                    elif item.get("document_type") in ["Server", "Database Server"]:
                        server_title = frappe.db.get_value(item.get("document_type"), document_name, "title")
                        if server_title:
                            item_name = f"Server: {server_title}"
                        else:
                            item_name = f"Server: {document_name}"
                    else:
                        item_name = document_name
                
                # Fallback: sử dụng description nếu có
                elif item.get("description") and str(item.get("description")).strip() not in ["", "None", "null"]:
                    item_name = str(item.get("description"))
                
                # LẤY SỐ LƯỢNG CHÍNH XÁC
                # Chỉ lấy phần nguyên của quantity để tránh số thập phân
                quantity = int(float(item.get("quantity", 1) or 1))
                if quantity <= 0:
                    quantity = 1
                
                # TÍNH GIÁ CHÍNH XÁC VÀ LÀM TRÒN
                item_amount = round(float(item.get("amount", 0) or 0))
                # Tính VAT cho từng item nếu cần
                if vat_percentage > 0 and not invoice_doc.get('amount_due_with_tax'):
                    item_amount = round(item_amount * (1 + vat_percentage / 100))
                
                # XỬ LÝ PRICE THEO CURRENCY
                if currency == 'VND':
                    # VND: Không nhân 100, sử dụng số tiền trực tiếp
                    item_price = int(item_amount)
                    print(f"📦 Item (VND): {item_name} | Qty: {quantity} | Price: {item_amount:,.0f} VND")
                else:
                    # USD/EUR: Nhân 100 để chuyển sang cents
                    item_price = int(item_amount * 100)
                    print(f"📦 Item ({currency}): {item_name} | Qty: {quantity} | Price: {item_amount:,.2f} {currency}")
                
                items.append({
                    "name": str(item_name)[:50],  # Giới hạn 50 ký tự
                    "quantity": quantity,
                    "price": item_price
                })
        
        # Nếu không có items hoặc items rỗng, tạo item mặc định
        if not items:
            if currency == 'VND':
                default_price = int(final_amount)
            else:
                default_price = int(final_amount * 100)
                
            items.append({
                "name": f"Invoice {invoice_name}",
                "quantity": 1,
                "price": default_price
            })
            print(f"📦 Default item: Invoice {invoice_name} | Qty: 1 | Price: {final_amount:,.0f} {currency}")

        # Prepare URLs (use defaults if not configured)
        cancel_url = payos_settings.get("payos_cancel_url") or "https://example.com/cancel"
        return_url = payos_settings.get("payos_return_url") or "https://example.com/success"
        
        # TỔNG SỐ TIỀN PAYOS - XỬ LÝ THEO CURRENCY
        if currency == 'VND':
            # VND: Không nhân 100, sử dụng số tiền trực tiếp
            payos_amount = int(final_amount)
            print(f"💳 Số tiền gửi lên PayOS (VND): {final_amount:,.0f} VND = {payos_amount:,}")
            print(f"📊 PayOS sẽ hiển thị: {payos_amount:,} VND (KHÔNG nhân 100)")
        else:
            # USD/EUR: Nhân 100 để chuyển sang cents
            payos_amount = int(final_amount * 100)
            print(f"💳 Số tiền gửi lên PayOS ({currency}): {final_amount:,.2f} {currency} = {payos_amount:,} cents")
            print(f"📊 PayOS sẽ hiển thị: {payos_amount:,} cents")
        
        # Chuẩn bị payload
        payment_data = {
            "orderCode": order_code,
            "amount": payos_amount,  # Số tiền đã xử lý đúng theo currency
            "description": f"Thanh toan hoa don {invoice_name}"[:25],  # Giới hạn 25 ký tự
            "buyerName": (invoice_doc.get("customer_name", "") or "")[:50] or "Customer",
            "buyerEmail": invoice_doc.get("customer_email", "") or invoice_doc.get("billing_email", "") or "test@example.com",
            "items": items,
            "cancelUrl": cancel_url,
            "returnUrl": return_url,
            "expiredAt": int((datetime.now() + timedelta(hours=24)).timestamp())  # Hết hạn sau 24h
        }

        # Tạo signature
        signature_data = {
            "amount": payment_data["amount"],
            "cancelUrl": payment_data["cancelUrl"],
            "description": payment_data["description"],
            "orderCode": payment_data["orderCode"],
            "returnUrl": payment_data["returnUrl"]
        }
        
        signature = generate_payos_signature(signature_data, payos_settings.get("payos_checksum_key", ""))
        if not signature:
            return {
                "success": False,
                "message": "Failed to generate signature",
                "error_code": "SIGNATURE_ERROR"
            }
        
        payment_data["signature"] = signature

        # Gửi request tới PayOS
        headers = {
            "x-client-id": payos_settings.get("payos_client_id", ""),
            "x-api-key": payos_settings.get("payos_api_key", ""),
            "Content-Type": "application/json"
        }

        print(f"🚀 Sending PayOS request for Invoice {invoice_name} - Order Code: {order_code}")
        print(f"📊 PayOS payload preview:")
        print(f"   - Amount: {payos_amount:,} ({currency})")
        print(f"   - Items count: {len(items)}")
        print(f"   - Description: {payment_data['description']}")
        
        response = requests.post(
            f"{PAYOS_BASE_URL}/v2/payment-requests",
            headers=headers,
            json=payment_data,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200 and response_data.get("code") == "00":
            # Lưu thông tin PayOS vào Invoice
            invoice_doc.db_set("payos_order_code", order_code)
            invoice_doc.db_set("payos_payment_link_id", response_data["data"].get("paymentLinkId"))
            invoice_doc.db_set("payos_checkout_url", response_data["data"].get("checkoutUrl"))
            invoice_doc.db_set("payos_qr_code", response_data["data"].get("qrCode"))
            invoice_doc.db_set("payos_status", "PENDING")
            
            print(f"✅ PayOS payment link created successfully: {order_code}")
            print(f"💰 Final amount: {final_amount:,.0f} {currency}")
            
            return {
                "success": True,
                "message": "Payment link created successfully",
                "data": {
                    "order_code": order_code,
                    "payment_link_id": response_data["data"].get("paymentLinkId"),
                    "checkout_url": response_data["data"].get("checkoutUrl"),
                    "qr_code": response_data["data"].get("qrCode"),
                    "amount": payment_data["amount"],
                    "amount_vnd": final_amount,  # Số tiền VND gốc
                    "currency": currency,
                    "items_count": len(items),
                    "description": payment_data["description"]
                }
            }
        else:
            print(f"❌ PayOS API Error: {response_data.get('desc', 'Unknown error')}")
            return {
                "success": False,
                "message": f"PayOS API Error: {response_data.get('desc', 'Unknown error')}",
                "error_code": response_data.get('code', 'UNKNOWN_ERROR'),
                "details": response_data
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error creating PayOS payment link")
        print(f"❌ Exception creating PayOS link: {str(e)}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }


def get_payos_payment_info(order_code_or_payment_id):
    """
    Lấy thông tin payment từ PayOS
    """
    try:
        payos_settings = check_payos_settings()
        if not payos_settings:
            return {
                "success": False,
                "message": "PayOS settings not configured",
                "error_code": "PAYOS_SETTINGS_MISSING"
            }

        headers = {
            "x-client-id": payos_settings.get("payos_client_id", ""),
            "x-api-key": payos_settings.get("payos_api_key", ""),
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{PAYOS_BASE_URL}/v2/payment-requests/{order_code_or_payment_id}",
            headers=headers,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200 and response_data.get("code") == "00":
            return {
                "success": True,
                "message": "Payment info retrieved successfully",
                "data": response_data["data"]
            }
        else:
            return {
                "success": False,
                "message": f"PayOS API Error: {response_data.get('desc', 'Unknown error')}",
                "error_code": response_data.get('code', 'UNKNOWN_ERROR')
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error getting PayOS payment info")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }


def cancel_payos_payment(order_code_or_payment_id, cancellation_reason="Cancelled by user"):
    """
    Hủy payment link PayOS
    """
    try:
        payos_settings = check_payos_settings()
        if not payos_settings:
            return {
                "success": False,
                "message": "PayOS settings not configured",
                "error_code": "PAYOS_SETTINGS_MISSING"
            }

        headers = {
            "x-client-id": payos_settings.get("payos_client_id", ""),
            "x-api-key": payos_settings.get("payos_api_key", ""),
            "Content-Type": "application/json"
        }

        payload = {
            "cancellationReason": cancellation_reason
        }

        response = requests.post(
            f"{PAYOS_BASE_URL}/v2/payment-requests/{order_code_or_payment_id}/cancel",
            headers=headers,
            json=payload,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200 and response_data.get("code") == "00":
            return {
                "success": True,
                "message": "Payment cancelled successfully",
                "data": response_data["data"]
            }
        else:
            return {
                "success": False,
                "message": f"PayOS API Error: {response_data.get('desc', 'Unknown error')}",
                "error_code": response_data.get('code', 'UNKNOWN_ERROR')
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error cancelling PayOS payment")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }


def update_invoice_payment_status(order_code, payment_data):
    """
    Cập nhật trạng thái Invoice sau khi nhận webhook từ PayOS
    """
    try:
        # Tìm Invoice bằng order_code
        invoice_result = frappe.db.get_value("Invoice", {"payos_order_code": order_code}, "name")
        
        if not invoice_result:
            frappe.log_error(f"Invoice not found for PayOS order code: {order_code}", "PayOS Webhook Error")
            return False

        # Ensure invoice_name is a string
        invoice_name = str(invoice_result) if invoice_result else None
        if not invoice_name:
            return False
            
        invoice_doc = frappe.get_doc("Invoice", invoice_name)
        
        # Cập nhật thông tin PayOS
        invoice_doc.db_set("payos_status", payment_data.get("code", ""))
        invoice_doc.db_set("payos_transaction_ref", payment_data.get("reference", ""))
        invoice_doc.db_set("payos_transaction_datetime", payment_data.get("transactionDateTime", ""))
        
        # Nếu thanh toán thành công
        if payment_data.get("code") == "00":
            invoice_doc.db_set("status", "Paid")
            invoice_doc.db_set("payment_date", datetime.now())
            invoice_doc.db_set("payment_mode", "PayOS")
            
            # ⚠️ SỬA LỖI CHÍNH: Xử lý đúng số tiền VND
            # PayOS trả về amount đã đúng cho VND, không cần chia 100
            payment_amount = float(payment_data.get("amount", 0))
            invoice_doc.db_set("amount_paid", payment_amount)  # Không chia 100 với VND
            
            # Tạo Payment Entry nếu cần
            create_payment_entry_for_invoice(invoice_doc, payment_data)
            
            frappe.log_error(f"Invoice {invoice_name} payment successful via PayOS", "PayOS Payment Success")
        
        return True

    except Exception as e:
        frappe.log_error(f"Error updating invoice payment status: {str(e)}", "PayOS Invoice Update Error")
        return False


def create_payment_entry_for_invoice(invoice_doc, payment_data):
    """
    Tạo Payment Entry cho Invoice sau khi thanh toán thành công
    """
    try:
        # Kiểm tra xem đã có Payment Entry chưa
        existing_payment = frappe.db.exists("Payment Entry", {
            "reference_no": payment_data.get("reference", ""),
            "party": invoice_doc.get("team", "")
        })
        
        if existing_payment:
            return existing_payment
        
        # ⚠️ SỬA LỖI: Xử lý đúng số tiền VND
        # PayOS trả về amount đã đúng cho VND, không cần chia 100
        payment_amount = float(payment_data.get("amount", 0))
        
        # Tạo Payment Entry mới
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": invoice_doc.get("team", ""),
            "paid_amount": payment_amount,  # Không chia 100 với VND
            "received_amount": payment_amount,  # Không chia 100 với VND
            "reference_no": payment_data.get("reference", ""),
            "reference_date": datetime.now().date(),
            "mode_of_payment": "PayOS",
            "remarks": f"Payment via PayOS for Invoice {invoice_doc.name}",
            "references": [{
                "reference_doctype": "Invoice",
                "reference_name": invoice_doc.name,
                "allocated_amount": payment_amount  # Không chia 100 với VND
            }]
        })
        
        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()
        
        return payment_entry.name

    except Exception as e:
        frappe.log_error(f"Error creating payment entry: {str(e)}", "PayOS Payment Entry Error")
        return None


def get_payment_status_display(payos_status, invoice_status):
    """
    Chuyển đổi status code thành text dễ hiểu
    """
    status_map = {
        "PENDING": "Chờ thanh toán",
        "00": "Đã thanh toán",
        "PAID": "Đã thanh toán", 
        "CANCELLED": "Đã hủy",
        "EXPIRED": "Đã hết hạn"
    }
    
    if payos_status in status_map:
        return status_map[payos_status]
    elif invoice_status == "Paid":
        return "Đã thanh toán"
    elif invoice_status == "Draft":
        return "Chờ xử lý"
    else:
        return "Không xác định"


def calculate_transaction_summary(filters):
    """
    Tính toán thống kê tổng quan cho giao dịch
    """
    try:
        # Get all matching invoices for summary
        summary_list = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN payos_status = '00' OR status = 'Paid' THEN 1 END) as successful_transactions,
                COUNT(CASE WHEN payos_status = 'PENDING' THEN 1 END) as pending_transactions,
                COUNT(CASE WHEN payos_status = 'CANCELLED' THEN 1 END) as cancelled_transactions,
                SUM(total) as total_amount,
                SUM(CASE WHEN payos_status = '00' OR status = 'Paid' THEN total ELSE 0 END) as successful_amount,
                SUM(CASE WHEN payos_status = 'PENDING' THEN total ELSE 0 END) as pending_amount,
                AVG(total) as average_amount
            FROM `tabInvoice`
            WHERE team = %(team)s 
            AND payos_order_code IS NOT NULL 
            AND payos_order_code != ''
        """, filters, as_dict=True)
        
        if summary_list and len(summary_list) > 0:
            summary = summary_list[0]
            total_trans = summary.get("total_transactions", 0) or 0
            successful_trans = summary.get("successful_transactions", 0) or 0
            
            return {
                "total_transactions": total_trans,
                "successful_transactions": successful_trans,
                "pending_transactions": summary.get("pending_transactions", 0) or 0,
                "cancelled_transactions": summary.get("cancelled_transactions", 0) or 0,
                "total_amount": float(summary.get("total_amount", 0) or 0),
                "successful_amount": float(summary.get("successful_amount", 0) or 0),
                "pending_amount": float(summary.get("pending_amount", 0) or 0),
                "average_amount": float(summary.get("average_amount", 0) or 0),
                "success_rate": round((successful_trans / max(total_trans, 1)) * 100, 2)
            }
    except Exception as e:
        frappe.log_error(f"Error calculating transaction summary: {str(e)}", "PayOS Summary Error")
    
    return {
        "total_transactions": 0,
        "successful_transactions": 0,
        "pending_transactions": 0,
        "cancelled_transactions": 0,
        "total_amount": 0.0,
        "successful_amount": 0.0,
        "pending_amount": 0.0,
        "average_amount": 0.0,
        "success_rate": 0.0
    }

