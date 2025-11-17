"""
Helper functions for app_marketing API
"""
import frappe
from press.utils import get_current_team_v2

def _enhance_with_table_fields(doctype, compressed_data):
    """
    Enhance compressed data với child table fields
    
    Args:
        doctype (str): Tên doctype
        compressed_data (dict): Data từ reportview.get() với format {keys: [], values: []}
    
    Returns:
        dict: Enhanced compressed data với table fields được append vào
    """
    # Tìm các Table fields trong doctype
    meta = frappe.get_meta(doctype)
    table_fields = [
        df.fieldname for df in meta.fields
        if df.fieldtype in ["Table", "Table MultiSelect"]
    ]
    
    if not table_fields:
        return compressed_data
    
    keys = list(compressed_data.get("keys", []))
    values = compressed_data.get("values", [])
    
    # Tìm index của field "name"
    name_index = keys.index("name") if "name" in keys else 0
    
    # Fetch child table data cho mỗi row
    enhanced_values = []
    for row in values:
        doc_name = row[name_index]
        full_doc = frappe.get_doc(doctype, doc_name)
        
        # Copy row hiện tại và append child table data
        new_row = list(row)
        for table_field in table_fields:
            child_data = full_doc.get(table_field, [])
            child_list = [child.as_dict() for child in child_data] if child_data else []
            new_row.append(child_list)
        
        enhanced_values.append(new_row)
    
    # Thêm table field names vào keys
    keys.extend(table_fields)
    
    return {
        "keys": keys,
        "values": enhanced_values
    }

def validate_team_access(arg_email=None):
    """
    Validate team access và System Manager role cho marketing API
    
    Args:
        arg_email (str): Email của user cần validate
        
    Returns:
        str: Team name nếu valid
        
    Raises:
        frappe.AuthenticationError: Nếu không có quyền truy cập
        frappe.PermissionError: Nếu không có role System Manager
    """
    if not arg_email:
        arg_email = frappe.session.user
    
    # Nếu user là Guest, throw error
    if arg_email == "Guest":
        frappe.throw(
            _("Authentication required. Please login."),
            frappe.AuthenticationError
        )
    
    # Check System Manager hoặc Press Admin role
    user_roles = frappe.get_roles(arg_email)
    if "System Manager" not in user_roles and "Press Admin" not in user_roles:
        frappe.throw(
            _("Only System Manager or Press Admin can access this API"),
            frappe.PermissionError
        )
    
    team = get_current_team_v2(arg_email, get_doc=False)
    if isinstance(team, dict) and team.get("error"):
        frappe.throw(
            _("Team validation failed: {0}").format(team.get("error")),
            frappe.AuthenticationError
        )
    return team