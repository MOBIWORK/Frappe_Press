import frappe

# Cache keys cho announcement data
ANNOUNCEMENT_CACHE_KEY = "mbw_announcements_all_data"
ANNOUNCEMENT_TIMESTAMP_KEY = "mbw_announcements_timestamp"

def clear_announcement_cache(doc=None, method=None):
	"""
	Xóa cache của announcements khi có update/delete
	
	Được gọi từ doc_events hooks (on_update, on_trash)
	Mục đích: Đảm bảo API trả về dữ liệu mới nhất sau khi có thay đổi
	
	Args:
		doc: Document instance (từ hooks)
		method: Event method (on_update, on_trash, etc.)
	"""
	try:
		cache = frappe.cache()
		
		# Clear data cache
		cache.delete_value(ANNOUNCEMENT_CACHE_KEY)
		
		# Clear timestamp cache
		cache.delete_value(ANNOUNCEMENT_TIMESTAMP_KEY)
		
		frappe.logger().info("Cleared announcement cache successfully")
		
	except Exception as e:
		frappe.log_error(
			message=frappe.get_traceback(),
			title="Error clearing announcement cache"
		)
