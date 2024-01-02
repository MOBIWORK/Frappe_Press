import frappe


def get_context(context):
    page_content = frappe.db.get_value('Custom Content Page', {'page_type': 'Thỏa thuận sử dụng dịch vụ'}, [
                                       'Content'])
    context.content = page_content if page_content else "Đang được cập nhật."
