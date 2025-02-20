import frappe
import time
from datetime import datetime
import redis
from contextlib import contextmanager

from press.utils import get_current_team

# Kết nối Redis từ Frappe config
REDIS_CLIENT = redis.StrictRedis.from_url(frappe.conf.redis_cache)


@contextmanager
def redis_lock_with_retry(lock_key, timeout=5, retry_interval=0.5):
    """Lock Redis và đợi nếu bị khóa"""
    lock = REDIS_CLIENT.lock(lock_key, timeout=timeout)
    
    while not lock.acquire(blocking=False):  # Không blocking, tránh deadlock
        pubsub = REDIS_CLIENT.pubsub()
        pubsub.subscribe(lock_key)  # Lắng nghe tín hiệu mở lock
        time.sleep(retry_interval)  # Đợi trước khi thử lại
    
    try:
        yield
    finally:
        lock.release()
        REDIS_CLIENT.publish(lock_key, "released")  # Phát tín hiệu lock mở


@frappe.whitelist(methods=['POST'])
def app_service_payment(**kwargs):
    user_lock_key = f"lock_{frappe.session.user}"
    try:
        # Lock theo user
        with redis_lock_with_retry(user_lock_key):
            team = get_current_team(True)
            
            price = 0
            service_name = kwargs.get('service_name')
            processing_unit = kwargs.get('processing_unit')
            type_service = kwargs.get('type')
            description = kwargs.get('description', '')
            # validate
            if not service_name:
                return {'code': 0,'msg': 'service_name is required!'}
            # ======
            if not processing_unit:
                return {'code': 0,'msg': 'processing_unit is required!'}
            
            doc_price = frappe.db.get_value('AI Service Price', {'app_name': service_name}, ['price'])
            if doc_price:
                price = doc_price
            else:
                return {'code': 0,'msg': f'service_name `{service_name}` not found!'}
            
            vat_percentage = frappe.db.get_single_value(
                    "Press Settings", "vat_percentage") or 0
            processing_unit = int(processing_unit)
            amount = price*processing_unit
            amount_vat = amount * vat_percentage / 100
            total_amount = amount + amount_vat
            
            # thêm log sử dụng
            doc = frappe.new_doc("Request Service AI")
            doc.team = team.name
            doc.service_name = service_name
            doc.description = description
            doc.start_time = datetime.now()
            doc.processing_unit = processing_unit
            doc.vat = vat_percentage
            doc.unit_price = price
            doc.insert(ignore_permissions=True)
            
            # get invoice
            invoice = team.get_upcoming_invoice()
            if not invoice:
                invoice = team.create_upcoming_invoice()
            
            # add item
            item_name = frappe.db.get_value('Invoice Item', {'parent': invoice.name,'document_type': 'Marketplace App', 'document_name': service_name, 'rate': price}, ['name', 'quantity'], as_dict=1)

            if not item_name:
                invoice.append('items', {
                    'document_type': 'Marketplace App',
                    'document_name': service_name,
                    'quantity': processing_unit,
                    'rate': price
                })
                invoice.save(ignore_permissions=True)
            else:
                frappe.db.set_value('Invoice Item', item_name.name, {
                    'quantity': item_name.quantity + processing_unit
                })
                invoice.reload()
                invoice.save(ignore_permissions=True)

            return {'code': 200, 'msg': 'Successfully'}
    
    except Exception as ex:
        frappe.db.rollback()
        frappe.log_error(f"Payment failed: {str(ex)}", "Service AI Payment Error")
        return {'code': 500,'msg': str(ex)}

@frappe.whitelist()
def get_user_balance():
    team = get_current_team(True)
    available_balances = team.available_balance()
    amount_all = team.get_balance_all()
    
    return {
        'balance': amount_all,
        'available_balances': available_balances
    }

@frappe.whitelist(methods=['POST'])
def sendmail_storage_capacity_overflows(**kwargs):
    try:
        team = get_current_team(True)
        user = frappe.db.get_value('User', team.user, ['first_name'], as_dict=1)
        site_name = kwargs.get('site_name')
        if not frappe.db.exists("Site",{"name": site_name, 'team': team.name}):
            return {'code': 0,'msg': 'site_name not found'}
        
        plan_name = frappe.db.get_value('Site', site_name, ['plan'])
        max_storage_usage = frappe.db.get_value('Plan', plan_name, ['max_storage_usage']) or 0
        max_storage_usage = round(max_storage_usage / 1024)
        date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        subject = f"""[EOVCloud] - Dung lượng lưu trữ website {site_name} của bạn đã đầy! - {date_time}"""
        args = {
            'user_name': user.first_name if user else team.user,
            'site_name': site_name,
            'link': f'https://eov.mbwcloud.com/dashboard/sites/{site_name}/overview',
            'max_storage_usage': max_storage_usage
        }
        email_recipients = team.user
        template = "storage_capacity_overflows"
        
        frappe.sendmail(
            recipients=email_recipients,
            subject=subject,
            template=template,
            args=args
        )
        
        return {'code': 200,'msg': 'Successfully'}
    except Exception as ex:
        frappe.log_error(f"{str(ex)}", "Sendmail storage capacity overflows")
        return {'code': 500,'msg': str(ex)}