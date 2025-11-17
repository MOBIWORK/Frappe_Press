import frappe
import json
from frappe import _
from mimetypes import guess_type
from frappe.utils import cint
from frappe.utils.image import optimize_image

from press.api.validators import validate_api_request
from press.api.app_marketing.api_helpers import _enhance_with_table_fields
from frappe.desk import reportview
from press.api.app_marketing.api_helpers import validate_team_access

ALLOWED_MIMETYPES = (
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
)

ALLOWED_DOCTYPES = [
    "Marketplace App Plan",
    "MBW Campaign Source",
    "MBW Voucher",
    "Invoice",
    "MBW Announcements Marketing",
]

@frappe.whitelist(allow_guest=True)
def upload_and_update_image():
    """
    API chuyên dụng: Upload ảnh và tự động update vào document
    
    Workflow:
    1. Upload file vào Press App
    2. Tạo File doctype record
    3. Auto update image field của document
    4. Return file_url
    
    Args (from form_dict):
        doctype (str): Tên doctype cần update (bắt buộc)
        docname (str): Tên document cần update (bắt buộc)
        fieldname (str): Tên field image, default: "image"
        is_private (int): File private (1) hay public (0), default: 0
        folder (str): Folder lưu file, default: "Home"
        optimize (bool): Tối ưu hóa ảnh, default: True
        max_width (int): Chiều rộng tối đa, default: 1200
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "file": {
                "file_url": str,
                "file_name": str
            },
            "doc": {
                "name": str,
                "image": str  # Updated image URL
            }
        }
    
    Examples:
        POST /api/method/press.api.app_marketing.api.upload_and_update_image
        Content-Type: multipart/form-data
        
        Form Data:
        - file: [binary file data]
        - doctype: "Marketplace App"
        - docname: "mbw_ats"
        - fieldname: "image"
    """
    try:
        # Lấy params từ query string (request.args) hoặc form_dict
        doctype = frappe.request.args.get('doctype') or frappe.form_dict.get('doctype')
        docname = frappe.request.args.get('docname') or frappe.form_dict.get('docname')
        fieldname = frappe.request.args.get('fieldname') or frappe.form_dict.get('fieldname', 'image')
        is_private = int(frappe.request.args.get('is_private', 0) or frappe.form_dict.get('is_private', 0))
        folder = frappe.request.args.get('folder') or frappe.form_dict.get('folder', 'Home')
        optimize_val = frappe.request.args.get('optimize', '1') or frappe.form_dict.get('optimize', '1')
        optimize = optimize_val in ['1', 'true', 'True', True]
        max_width = int(frappe.request.args.get('max_width', 1200) or frappe.form_dict.get('max_width', 1200))
        
        # Validate file upload
        if not frappe.request.files or 'file' not in frappe.request.files:
            return {
                "success": False,
                "message": "No file uploaded. Please upload a file with key 'file'",
                "error_code": "MISSING_FILE"
            }
        
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not docname:
            return {
                "success": False,
                "message": "Parameter 'docname' is required",
                "error_code": "MISSING_DOCNAME"
            }
        
        arg_email = frappe.request.args.get('arg_email') or frappe.form_dict.get('arg_email') or frappe.session.user
        
        # Validate quyền truy cập của user
        try:
            validate_team_access(arg_email=arg_email)
        except frappe.AuthenticationError as e:
            return {
                "success": False,
                "message": str(e),
                "error_code": "AUTHENTICATION_ERROR"
            }
        except frappe.PermissionError as e:
            return {
                "success": False,
                "message": str(e),
                "error_code": "PERMISSION_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Validation error: {str(e)}",
                "error_code": "VALIDATION_ERROR"
            }
        
        # Bước 1: Upload file vào storage
        upload_result = upload_file(
            arg_email=arg_email,
            is_private=is_private,
            folder=folder,
            optimize=optimize,
            max_width=max_width,
            doctype=doctype,
            docname=docname,
            fieldname=fieldname
        )
        
        if not upload_result.get("success"):
            return upload_result
        
        file_url = upload_result["file"]["file_url"]
        
        # Bước 2: Update field image của document
        doc = frappe.get_doc(doctype, docname)
        doc.set(fieldname, file_url)
        doc.save(ignore_permissions=True)
        doc.reload()
        
        return {
            "success": True,
            "message": f"Image uploaded and {doctype} updated successfully",
            "file": upload_result["file"],
            "doc": {
                "name": doc.name,
                fieldname: doc.get(fieldname)
            }
        }
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"Document '{docname}' not found in {doctype}",
            "error_code": "DOCUMENT_NOT_FOUND"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in upload_and_update_image")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist(methods=["POST"])
def upload_file(arg_email=None, is_private=0, folder="Home", optimize=False, 
                max_width=None, max_height=None, doctype=None, docname=None, fieldname=None):
    """
    REST API để upload file lên hệ thống Frappe
    
    Args:
        arg_email (str): Email của user để xác định team
        is_private (int): File private (1) hay public (0), default: 0
        folder (str): Folder lưu file, default: "Home"
        optimize (bool): Tối ưu hóa ảnh (chỉ áp dụng cho image), default: False
        max_width (int): Chiều rộng tối đa khi optimize ảnh
        max_height (int): Chiều cao tối đa khi optimize ảnh
        doctype (str): Doctype để attach file (optional)
        docname (str): Document name để attach file (optional)
        fieldname (str): Field name để attach file (optional)
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "file": {
                "file_url": str,      # URL của file
                "file_name": str,     # Tên file
                "is_private": int,    # Private flag
                "file_size": int,     # Kích thước file (bytes)
                "content_type": str   # MIME type
            }
        }
    
    Examples:
        # Upload ảnh cho Marketplace App
        POST /api/method/press.api.app_marketing.api.upload_file
        Content-Type: multipart/form-data
        
        Form Data:
        - file: [binary file data]
        - is_private: 0
        - folder: "Home"
        - optimize: true
        - max_width: 1200
        - doctype: "Marketplace App"
        - docname: "mbw_ats"
        - fieldname: "image"
    """
    try:
        # Validate team access
        validate_team_access(arg_email)
        
        # Kiểm tra file có được upload không
        if not frappe.request.files or "file" not in frappe.request.files:
            return {
                "success": False,
                "message": "No file uploaded. Please provide a file in 'file' field",
                "error_code": "NO_FILE_UPLOADED"
            }
        
        file = frappe.request.files["file"]
        content = file.stream.read()
        filename = file.filename
        
        if not filename:
            return {
                "success": False,
                "message": "Filename is required",
                "error_code": "MISSING_FILENAME"
            }
        
        # Validate file type
        content_type = guess_type(filename)[0]
        if content_type not in ALLOWED_MIMETYPES:
            return {
                "success": False,
                "message": f"File type '{content_type}' is not allowed. Allowed types: images, PDF, Word, Excel, CSV, TXT",
                "error_code": "INVALID_FILE_TYPE"
            }
        
        # Optimize image nếu cần
        if optimize and content_type and content_type.startswith("image/"):
            args = {"content": content, "content_type": content_type}
            if max_width:
                args["max_width"] = int(max_width)
            if max_height:
                args["max_height"] = int(max_height)
            try:
                content = optimize_image(**args)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Image Optimization Error")
                pass
        
        # Tạo File document
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "folder": folder,
            "is_private": cint(is_private),
            "content": content,
            "attached_to_doctype": doctype,
            "attached_to_name": docname,
            "attached_to_field": fieldname,
        })
        
        # Set owner to arg_email để user có quyền access file
        if arg_email:
            file_doc.owner = arg_email
        
        file_doc.save(ignore_permissions=True)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": {
                "file_url": file_doc.file_url,
                "file_name": file_doc.file_name,
                "is_private": file_doc.is_private,
                "file_size": file_doc.file_size,
                "content_type": content_type
            }
        }
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), "Authentication Error in upload_file")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), "Permission Error in upload_file")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in upload_file API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def get_list(doctype=None, fields=None, include_table_fields=False, arg_email=None, **kwargs):
    """
    REST API GENERIC để lấy danh sách bản ghi của BẤT KỲ doctype nào
    Args:
        doctype (str): Tên doctype cần lấy dữ liệu (bắt buộc)
        fields (str/list): Danh sách fields cần lấy (optional). Có thể là:
            - None hoặc []: Lấy tất cả fields (default behavior)
            - String: "name,title,status" hoặc '["name","title","status"]'
            - List: ["name", "title", "status"]
        arg_email (str): Email của user để xác định team
        include_table_fields (bool): Cho phép lấy cả Table fields (chỉ áp dụng cho một số doctype được phép)
        **kwargs: Tất cả parameters khác sẽ được xử lý bởi Frappe core
            - filters (str/list/dict): Filters để lọc dữ liệu
            - order_by (str): Sắp xếp kết quả
            - limit_start (int): Vị trí bắt đầu
            - limit_page_length (int): Số lượng bản ghi
            - distinct (bool): Lấy giá trị distinct
            - group_by (str): Group by field
            - or_filters (list): OR filters
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "data": {
                "keys": list,
                "values": list,
                "user_info": dict,
                "total_count": int,
                "limit_start": int,
                "limit_page_length": int
            }
        }
    """
    try:
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        # Clean up parameters không dùng cho reportview
        for param in ["arg_email", "doctype", "include_table_fields", "fields"]:
            kwargs.pop(param, None)
        
        # Convert include_table_fields sang boolean
        if isinstance(include_table_fields, str):
            include_table_fields = include_table_fields.lower() in ['true', '1', 'yes']
        else:
            include_table_fields = bool(include_table_fields)
        
        # Validate team access
        if not arg_email:
            arg_email = frappe.session.user
        
        if arg_email not in ['Guest', 'Administrator', None]:
            validate_team_access(arg_email)
        
        # Set default pagination
        kwargs.setdefault("limit_page_length", 20)
        kwargs.setdefault("limit_start", 0)
        
        # Doctype whitelist cho Table fields
        list_doctype = ALLOWED_DOCTYPES
        
        # Process fields parameter
        requested_fields = None
        if fields:
            # Parse fields nếu là string
            if isinstance(fields, str):
                if fields.strip().startswith('['):
                    try:
                        fields = json.loads(fields)
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "message": "Invalid JSON format for 'fields' parameter",
                            "error_code": "INVALID_FIELDS_FORMAT"
                        }
                else:
                    fields = [f.strip() for f in fields.split(',')]
            
            # Validate fields là list
            if not isinstance(fields, list):
                return {
                    "success": False,
                    "message": "Parameter 'fields' must be a list or comma-separated string",
                    "error_code": "INVALID_FIELDS_TYPE"
                }
            
            # Nếu fields không rỗng, validate và sử dụng
            if fields:
                # Ensure 'name' field is always included
                if 'name' not in fields:
                    fields = ['name'] + fields
                
                # Validate fields tồn tại trong doctype
                meta = frappe.get_meta(doctype)
                valid_fieldnames = {df.fieldname for df in meta.fields if df.fieldname}
                valid_fieldnames.add('name')
                
                invalid_fields = [f for f in fields if f not in valid_fieldnames]
                if invalid_fields:
                    return {
                        "success": False,
                        "message": f"Invalid fields for {doctype}: {', '.join(invalid_fields)}",
                        "error_code": "INVALID_FIELDS",
                        "invalid_fields": invalid_fields
                    }
                
                requested_fields = fields
                kwargs["fields"] = json.dumps(fields)
        
        # Fields list nếu không được truyền chỉ định (lấy tất cả)
        if not kwargs.get("fields"):
            meta = frappe.get_meta(doctype)
            
            # Fieldtypes cần loại bỏ (Table fields sẽ fetch riêng sau)
            EXCLUDED_FIELDTYPES = {
                "Table", "Table MultiSelect", "HTML", "Button",
                "Column Break", "Section Break", "Tab Break", "Fold", "Heading"
            }
            
            standard_fields = ["name", "owner", "creation", "modified", "modified_by", "idx", "docstatus"]
            
            # Custom fields từ meta
            custom_fields = [
                df.fieldname for df in meta.fields
                if df.fieldname and df.fieldtype not in EXCLUDED_FIELDTYPES
            ]
            valid_fields = standard_fields + [f for f in custom_fields if f not in standard_fields]
            
            kwargs["fields"] = json.dumps(valid_fields)
        
        # Update form_dict cho reportview
        frappe.local.form_dict["doctype"] = doctype
        frappe.local.form_dict.update(kwargs)
        
        for param in ["include_table_fields", "arg_email"]:
            frappe.local.form_dict.pop(param, None)
        
        original_user = frappe.session.user
        if arg_email and arg_email not in ['Guest', None]:
            frappe.session.user = arg_email
        
        try:
            # Fetch data từ reportview
            compressed_data = reportview.get()
            total_count = reportview.get_count()
            args = reportview.get_form_params()
            
            if not isinstance(compressed_data, dict):
                compressed_data = {
                    "keys": [],
                    "values": compressed_data if isinstance(compressed_data, list) else [],
                    "user_info": {}
                }
            
            if include_table_fields and doctype in list_doctype:
                compressed_data = _enhance_with_table_fields(
                    doctype, compressed_data
                )
            
            response_data = {
                "keys": compressed_data.get("keys", []),
                "values": compressed_data.get("values", []),
                "user_info": compressed_data.get("user_info", {}),
                "total_count": total_count,
                "limit_start": args.get("limit_start", 0),
                "limit_page_length": args.get("limit_page_length", 20)
            }
            
            # Thêm requested_fields vào response nếu user chỉ định fields cụ thể
            if requested_fields:
                response_data["requested_fields"] = requested_fields
            
            return {
                "success": True,
                "message": f"Data retrieved successfully from {doctype}",
                "data": response_data
            }
        finally:
            frappe.session.user = original_user
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in get_list for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in get_list for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_list API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def get_doc(doctype=None, name=None, arg_email=None):
    """
    REST API GENERIC để lấy chi tiết 1 bản ghi doctype
    
    Args:
        doctype (str): Tên doctype (bắt buộc)
        name (str): Tên/ID của bản ghi (bắt buộc)
        arg_email (str): Email của user để xác định team
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "doc": dict  # Document data
        }
    
    Examples:
        # Lấy chi tiết Marketplace App
        GET /api/method/press.api.app_marketing.api.get_doc?doctype=Marketplace App&name=mbw_ats
        
        # Lấy chi tiết User
        GET /api/method/press.api.app_marketing.api.get_doc?doctype=User&name=user@example.com
    """
    try:
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not name:
            return {
                "success": False,
                "message": "Parameter 'name' is required",
                "error_code": "MISSING_NAME"
            }
        
        validate_team_access(arg_email)
        doc = frappe.get_doc(doctype, name)
        
        # Check read permission
        if not doc.has_permission("read"):
            frappe.throw(
                _("Insufficient Permission for {0}").format(f"{doctype} {name}"),
                frappe.PermissionError
            )
        doc_dict = doc.as_dict()
        
        return {
            "success": True,
            "message": f"Document retrieved successfully from {doctype}",
            "doc": doc_dict
        }
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"Document '{name}' not found in {doctype}",
            "error_code": "DOCUMENT_NOT_FOUND"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in get_doc for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in get_doc for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_doc API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def get_doctype_info(doctype=None, arg_email=None):
    """
    REST API GENERIC để lấy thông tin metadata của doctype
    Bao gồm: fields, permissions, settings, links, etc.
    
    Args:
        doctype (str): Tên doctype (bắt buộc)
        arg_email (str): Email của user để xác định team
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "doctype_info": {
                "name": str,
                "module": str,
                "fields": list,
                "permissions": list,
                "links": list,
                "actions": list,
                "is_submittable": bool,
                "is_tree": bool,
                "is_single": bool,
                "track_changes": bool,
                ...
            }
        }
    
    Examples:
        # Lấy thông tin Marketplace App doctype
        GET /api/method/press.api.app_marketing.api.get_doctype_info?doctype=Marketplace App
        
        # Lấy thông tin User doctype
        GET /api/method/press.api.app_marketing.api.get_doctype_info?doctype=User
    """
    try:
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        validate_team_access(arg_email)
        meta = frappe.get_meta(doctype)
        meta_dict = meta.as_dict()

        from frappe.permissions import get_valid_perms
        permissions = get_valid_perms(doctype)
        
        links = frappe.get_all(
            "DocType Link",
            filters={"parent": doctype},
            fields=["link_doctype", "link_fieldname", "table_fieldname", "group"]
        )
        
        # Lấy actions (custom buttons/actions)
        actions = frappe.get_all(
            "DocType Action",
            filters={"parent": doctype},
            fields=["label", "action_type", "action", "hidden"]
        )

        doctype_info = {
            "name": meta_dict.get("name"),
            "module": meta_dict.get("module"),
            "app": frappe.local.module_app.get(meta_dict.get("module")),
            "custom": meta_dict.get("custom", 0),
            "istable": meta_dict.get("istable", 0),
            "issingle": meta_dict.get("issingle", 0),
            "is_submittable": meta_dict.get("is_submittable", 0),
            "is_tree": meta_dict.get("is_tree", 0),
            "editable_grid": meta_dict.get("editable_grid", 0),
            "track_changes": meta_dict.get("track_changes", 0),
            "track_seen": meta_dict.get("track_seen", 0),
            "track_views": meta_dict.get("track_views", 0),
            "fields": meta_dict.get("fields", []),
            "permissions": permissions,
            "links": links,
            "actions": actions,
            "title_field": meta_dict.get("title_field"),
            "image_field": meta_dict.get("image_field"),
            "sort_field": meta_dict.get("sort_field", "modified"),
            "sort_order": meta_dict.get("sort_order", "DESC"),
            "default_print_format": meta_dict.get("default_print_format"),
            "autoname": meta_dict.get("autoname"),
            "naming_rule": meta_dict.get("naming_rule"),
            "description": meta_dict.get("description"),
            "documentation": meta_dict.get("documentation"),
            "allow_copy": meta_dict.get("allow_copy", 0),
            "allow_import": meta_dict.get("allow_import", 0),
            "allow_rename": meta_dict.get("allow_rename", 0),
            "show_preview_popup": meta_dict.get("show_preview_popup", 0),
            "max_attachments": meta_dict.get("max_attachments", 0),
        }
        
        return {
            "success": True,
            "message": f"DocType info retrieved successfully for {doctype}",
            "doctype_info": doctype_info
        }
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"DocType '{doctype}' not found",
            "error_code": "DOCTYPE_NOT_FOUND"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in get_doctype_info for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in get_doctype_info for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_doctype_info API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True, methods=["POST", "PUT"])
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def update_doc(doctype=None, name=None, doc_data=None, arg_email=None):
    """
    REST API GENERIC để cập nhật thông tin bản ghi của doctype
    Args:
        doctype (str): Tên doctype (bắt buộc)
        name (str): Tên/ID của bản ghi (bắt buộc)
        doc_data (dict): Dữ liệu cần cập nhật (bắt buộc)
        arg_email (str): Email của user để xác định team
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "doc": dict  # Document data sau khi update
        }
    
    Examples:
        # Cập nhật Marketplace App
        POST /api/method/press.api.app_marketing.api.update_doc
        Body: {
            "doctype": "Marketplace App",
            "name": "mbw_ats",
            "doc_data": {
                "title": "New Title",
                "status": "Published",
                "description": "Updated description"
            }
        }
        
        # Cập nhật image cho Marketplace App (Attach Image field)
        # Lưu ý: File phải được upload lên hệ thống trước
        # Sử dụng API: press.api.app_marketing.api.upload_file
        POST /api/method/press.api.app_marketing.api.update_doc
        Body: {
            "doctype": "Marketplace App",
            "name": "mbw_ats",
            "doc_data": {
                "image": "/files/app_logo.png"  # file_url từ upload_file API
            }
        }
    """
    try:
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not name:
            return {
                "success": False,
                "message": "Parameter 'name' is required",
                "error_code": "MISSING_NAME"
            }
        
        if not doc_data:
            return {
                "success": False,
                "message": "Parameter 'doc_data' is required",
                "error_code": "MISSING_DOC_DATA"
            }
        
        validate_team_access(arg_email)
        
        if isinstance(doc_data, str):
            doc_data = json.loads(doc_data)

        doc = frappe.get_doc(doctype, name)
        if not doc.has_permission("write"):
            frappe.throw(
                _("Insufficient Permission to update {0}").format(f"{doctype} {name}"),
                frappe.PermissionError
            )
        
        for field, value in doc_data.items():
            # Không cho phép update các field system
            if field not in ["name", "owner", "creation", "modified", "modified_by", "doctype", "docstatus"]:
                doc.set(field, value)
        doc_json = frappe.as_json(doc.as_dict())
        from frappe.desk.form.save import savedocs
        
        frappe.local.response.docs = []
        savedocs(doc=doc_json, action="Save")
        if frappe.local.response.docs:
            updated_doc = frappe.local.response.docs[0]
        else:
            doc.reload()
            updated_doc = doc.as_dict()
        
        return {
            "success": True,
            "message": f"Document updated successfully in {doctype}",
            "doc": updated_doc
        }
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"Document '{name}' not found in {doctype}",
            "error_code": "DOCUMENT_NOT_FOUND"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in update_doc for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in update_doc for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), f"Validation Error in update_doc for {doctype}")
        return {
            "success": False,
            "message": f"Validation error: {str(e)}",
            "error_code": "VALIDATION_ERROR"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in update_doc API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True, methods=["POST", "DELETE"])
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 50, "window": 3600}
)
def delete_items(doctype=None, items=None, arg_email=None):
    """
    REST API để xóa nhiều bản ghi trong doctype
    
    Args:
        doctype (str): Tên doctype cần xóa (bắt buộc)
        items (list/str): Danh sách tên/ID các bản ghi cần xóa (bắt buộc)
            - Có thể là JSON array: ["name1", "name2", "name3"]
            - Hoặc list: ["name1", "name2"]
        arg_email (str): Email của user để xác định team và quyền
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "deleted_count": int,
            "total_requested": int
        }
    
    Examples:
        # Xóa một Marketplace App Plan
        POST /api/method/press.api.app_marketing.api.delete_items
        Body: {
            "doctype": "Marketplace App Plan",
            "items": ["plan-001"]
        }
        
        # Xóa nhiều MBW Voucher
        POST /api/method/press.api.app_marketing.api.delete_items
        Body: {
            "doctype": "MBW Voucher",
            "items": ["voucher-001", "voucher-002", "voucher-003"]
        }
    """
    try:
        # Validate required parameters
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not items:
            return {
                "success": False,
                "message": "Parameter 'items' is required",
                "error_code": "MISSING_ITEMS"
            }
        
        # Validate team access
        validate_team_access(arg_email)
        
        # Parse items nếu là string
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"Invalid JSON in items: {str(e)}",
                    "error_code": "INVALID_JSON"
                }
        
        # Validate items là list
        if not isinstance(items, list):
            return {
                "success": False,
                "message": "Parameter 'items' must be a list or JSON array",
                "error_code": "INVALID_ITEMS_TYPE"
            }
        
        if len(items) == 0:
            return {
                "success": False,
                "message": "Items list cannot be empty",
                "error_code": "EMPTY_ITEMS_LIST"
            }
        
        # Validate doctype exists
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "message": f"DocType '{doctype}' does not exist",
                "error_code": "DOCTYPE_NOT_FOUND"
            }
        
        # Set user context cho delete operations
        original_user = frappe.session.user
        if arg_email and arg_email not in ['Guest', None]:
            frappe.session.user = arg_email
        
        try:
            # Thực hiện bulk delete với error tracking
            deleted_count = 0
            failed_items = []
            
            # Sort reverse để xóa từ cuối lên (tránh ảnh hưởng index)
            items_to_delete = sorted(items, reverse=True)
            
            for item_name in items_to_delete:
                try:
                    # Check quyền delete cho từng item
                    doc = frappe.get_doc(doctype, item_name)
                    if not doc.has_permission("delete"):
                        failed_items.append({
                            "name": item_name,
                            "reason": "Insufficient permission to delete"
                        })
                        continue
                    
                    # Xóa document
                    frappe.delete_doc(doctype, item_name)
                    deleted_count += 1
                    
                    # Publish progress cho UI (nếu >= 5 items)
                    if len(items_to_delete) >= 5:
                        frappe.publish_realtime(
                            "progress",
                            dict(
                                progress=[deleted_count, len(items_to_delete)],
                                title=_("Deleting {0}").format(doctype),
                                description=item_name
                            ),
                            user=frappe.session.user,
                        )
                    
                    # Commit sau mỗi lần xóa thành công
                    frappe.db.commit()
                    
                except frappe.DoesNotExistError:
                    failed_items.append({
                        "name": item_name,
                        "reason": f"Document not found"
                    })
                    frappe.db.rollback()
                except frappe.PermissionError as pe:
                    failed_items.append({
                        "name": item_name,
                        "reason": f"Permission denied: {str(pe)}"
                    })
                    frappe.db.rollback()
                except frappe.LinkExistsError as le:
                    failed_items.append({
                        "name": item_name,
                        "reason": f"Cannot delete - linked documents exist: {str(le)}"
                    })
                    frappe.db.rollback()
                except Exception as e:
                    failed_items.append({
                        "name": item_name,
                        "reason": f"Delete failed: {str(e)}"
                    })
                    frappe.db.rollback()
            
            # Xây dựng response message
            if deleted_count == len(items_to_delete):
                message = f"Successfully deleted all {deleted_count} items from {doctype}"
                success = True
            elif deleted_count > 0:
                message = f"Deleted {deleted_count} out of {len(items_to_delete)} items from {doctype}"
                success = True
            else:
                message = f"Failed to delete any items from {doctype}"
                success = False
            
            return {
                "success": success,
                "message": message,
                "deleted_count": deleted_count,
                "total_requested": len(items_to_delete)
            }
            
        finally:
            # Restore user context
            frappe.session.user = original_user
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"DocType '{doctype}' does not exist",
            "error_code": "DOCTYPE_NOT_FOUND"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in delete_items for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in delete_items for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in delete_items API for {doctype}")
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
def get_record_activities(doctype=None, name=None, arg_email=None, limit_start=0, limit_page_length=20):
    """
    REST API lấy thông tin activities và attachments của một bản ghi
    
    Args:
        doctype (str): Tên doctype (bắt buộc)
        name (str): Tên/ID của bản ghi (bắt buộc)
        arg_email (str): Email của user để xác định team
        limit_start (int): Vị trí bắt đầu phân trang (default: 0)
        limit_page_length (int): Số lượng activities trả về (default: 20, max: 100)
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "data": {
                "activities": list,      # Danh sách activities đã được phân trang
                "attachments": list,     # Danh sách attachments
                "total_count": int,      # Tổng số activities
                "limit_start": int,      # Vị trí bắt đầu
                "limit_page_length": int # Số lượng trả về
            }
        }
    """
    try:
        if not doctype:
            frappe.local.response.http_status_code = 400
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not name:
            frappe.local.response.http_status_code = 400
            return {
                "success": False,
                "message": "Parameter 'name' is required",
                "error_code": "MISSING_NAME"
            }
        validate_team_access(arg_email)
        user_roles = frappe.get_roles(arg_email)
        try:
            if "System Manager" in user_roles or "Press Admin" in user_roles:
                frappe.set_user(arg_email)
                doc = frappe.get_doc(doctype, name)
            else :
                frappe.local.response.http_status_code = 403
                return {
                    "success": False,
                    "message": "Only System Manager or Press Admin can access this API",
                    "error_code": "PERMISSION_DENIED"
                }
        except frappe.DoesNotExistError:
            frappe.local.response.http_status_code = 404
            return {
                "success": False,
                "message": f"Document '{name}' not found in {doctype}",
                "error_code": "DOCUMENT_NOT_FOUND"
            }
        except Exception as e:
            frappe.local.response.http_status_code = 500
            return {
                "success": False,
                "message": f"Error accessing document: {str(e)}",
                "error_code": "DOCUMENT_ACCESS_ERROR"
            }
        
        # Validate and sanitize pagination parameters
        try:
            limit_start = int(limit_start) if limit_start else 0
            limit_page_length = int(limit_page_length) if limit_page_length else 20
        except (ValueError, TypeError):
            frappe.local.response.http_status_code = 400
            return {
                "success": False,
                "message": "Invalid pagination parameters. limit_start and limit_page_length must be integers",
                "error_code": "INVALID_PAGINATION"
            }
        
        # Enforce max limit để tránh overload
        MAX_LIMIT = 100
        if limit_page_length > MAX_LIMIT:
            limit_page_length = MAX_LIMIT
        
        if limit_start < 0:
            limit_start = 0

        from press.api.app_marketing.activities_handler import get_record_activities
        
        # Get activities và attachments
        try:
            activities, attachments = get_record_activities(doctype, name)
        except frappe.DoesNotExistError:
            frappe.local.response.http_status_code = 404
            return {
                "success": False,
                "message": f"Document '{name}' not found in {doctype}",
                "error_code": "DOCUMENT_NOT_FOUND"
            }
        except Exception as handler_error:
            frappe.log_error(frappe.get_traceback(), f"Error in activities_handler for {doctype}")
            frappe.local.response.http_status_code = 500
            return {
                "success": False,
                "message": f"Failed to retrieve activities: {str(handler_error)}",
                "error_code": "HANDLER_ERROR"
            }
        total_count = len(activities)
        end_index = limit_start + limit_page_length
        paginated_activities = activities[limit_start:end_index]
        
        return {
            "success": True,
            "message": f"Activities retrieved successfully for {doctype} {name}",
            "data": {
                "activities": paginated_activities,
                "attachments": attachments,
                "total_count": total_count,
                "limit_start": limit_start,
                "limit_page_length": limit_page_length,
                "has_more": end_index < total_count
            }
        }
        
    except frappe.DoesNotExistError:
        frappe.local.response.http_status_code = 404
        return {
            "success": False,
            "message": f"Document '{name}' not found in {doctype}",
            "error_code": "DOCUMENT_NOT_FOUND"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in get_record_activities for {doctype}")
        frappe.local.response.http_status_code = 401
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in get_record_activities for {doctype}")
        frappe.local.response.http_status_code = 403
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_record_activities API for {doctype}")
        frappe.local.response.http_status_code = 500
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True)
def insert_doc(doctype=None, doc_data=None, arg_email=None):
    """
    REST API GENERIC để insert bản ghi mới vào bất kỳ doctype nào

    Args:
        doctype (str): Tên doctype (bắt buộc)
        doc_data (dict/str): Dữ liệu document cần insert (bắt buộc)
        arg_email (str): Email của user để xác định team
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
        }
    """
    try:
        # Validate required parameters
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        if not doc_data:
            return {
                "success": False,
                "message": "Parameter 'doc_data' is required",
                "error_code": "MISSING_DOC_DATA"
            }
        validate_team_access(arg_email)
        if isinstance(doc_data, str):
            try:
                doc_data = json.loads(doc_data)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"Invalid JSON in doc_data: {str(e)}",
                    "error_code": "INVALID_JSON"
                }
        if not isinstance(doc_data, dict):
            return {
                "success": False,
                "message": "doc_data must be a dictionary or valid JSON string",
                "error_code": "INVALID_DOC_DATA_TYPE"
            }
        doc_data["doctype"] = doctype
        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        doc.reload()
        
        return {
            "success": True,
            "message": f"Document inserted successfully in {doctype}",
        }
        
    except frappe.DuplicateEntryError as e:
        frappe.log_error(frappe.get_traceback(), f"Duplicate Entry Error in insert_doc for {doctype}")
        return {
            "success": False,
            "message": f"Duplicate entry: {str(e)}",
            "error_code": "DUPLICATE_ENTRY"
        }
    except frappe.MandatoryError as e:
        frappe.log_error(frappe.get_traceback(), f"Mandatory Error in insert_doc for {doctype}")
        return {
            "success": False,
            "message": f"Missing mandatory fields: {str(e)}",
            "error_code": "MANDATORY_ERROR"
        }
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), f"Validation Error in insert_doc for {doctype}")
        return {
            "success": False,
            "message": f"Validation error: {str(e)}",
            "error_code": "VALIDATION_ERROR"
        }
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in insert_doc for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in insert_doc for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except frappe.DoesNotExistError as e:
        frappe.log_error(frappe.get_traceback(), f"DocType Not Found in insert_doc")
        return {
            "success": False,
            "message": f"DocType '{doctype}' does not exist",
            "error_code": "DOCTYPE_NOT_FOUND"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in insert_doc API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def get_count(doctype=None, arg_email=None, **kwargs):
    """
    Args:
        doctype (str): Tên doctype cần đếm (bắt buộc)
        **kwargs: Tất cả parameters khác sẽ được xử lý bởi Frappe core
            - filters (str/list/dict): Filters để lọc dữ liệu
            - distinct (bool): Đếm giá trị distinct
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "count": int
        }
    
    Examples:
        # Đếm Marketplace Apps
        GET /api/method/press.api.app_marketing.api.get_count?doctype=Marketplace App
        
        # Đếm Active Sites
        GET /api/method/press.api.app_marketing.api.get_count?doctype=Site&filters=[["status","=","Active"]]
    """
    try:
        # Validate doctype parameter
        if not doctype:
            return {
                "success": False,
                "message": "Parameter 'doctype' is required",
                "error_code": "MISSING_DOCTYPE"
            }
        
        frappe.local.form_dict["doctype"] = doctype
        
        # Loại bỏ arg_email khỏi kwargs vì reportview không nhận parameter này
        kwargs.pop("arg_email", None)
        
        frappe.local.form_dict.update(kwargs)
        count = reportview.get_count()
        
        return {
            "success": True,
            "message": f"Count retrieved successfully from {doctype}",
            "count": count
        }
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), f"Authentication Error in get_count for {doctype}")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in get_count for {doctype}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_count API for {doctype}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }

@frappe.whitelist(allow_guest=True, methods=["POST"])
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 50, "window": 3600}
)
def submit_invoice(invoice_name=None, arg_email=None):
    """
    REST API để submit Invoice từ app khác
    
    Args:
        invoice_name (str): Tên Invoice cần submit (bắt buộc)
        arg_email (str): Email của user để xác định quyền (optional, default: current user)
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
        }
    """
    try:
        if not invoice_name:
            return {
                "success": False,
                "message": "Parameter 'invoice_name' is required",
                "error_code": "MISSING_INVOICE_NAME"
            }
        
        if arg_email and arg_email != "Guest":
            frappe.set_user(arg_email)
            
        doc = frappe.get_doc("Invoice", invoice_name)
        if doc.docstatus != 0:
            return {
                "success": False,
                "message": f"Invoice {invoice_name} is already submitted or cancelled",
                "error_code": "INVALID_DOCSTATUS",
                "current_docstatus": doc.docstatus
            }
        doc.submit()
        # Update giá trị custom_status_einvoice thành "Issued" sau khi submit
        doc.db_set("custom_status_einvoice", "Issued", update_modified=False)
        doc.reload()
        
        return {
            "success": True,
            "message": f"Invoice {invoice_name} submitted successfully",
        }
        
    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": f"Invoice '{invoice_name}' not found",
            "error_code": "INVOICE_NOT_FOUND"
        }
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), f"Validation Error in submit_invoice for {invoice_name}")
        return {
            "success": False,
            "message": f"Validation error: {str(e)}",
            "error_code": "VALIDATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), f"Permission Error in submit_invoice for {invoice_name}")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in submit_invoice API for {invoice_name}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist(allow_guest=True)
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 100, "window": 3600}
)
def get_marketing_announcements(name_app=None, site=None, arg_email=None):
    """
    REST API để lấy danh sách thông báo marketing mà app được phép xem
    
    Validation logic:
    - Field 'app' trong announcement:
        + Nếu rỗng -> thông báo áp dụng cho TẤT CẢ app (app này được xem)
        + Nếu có giá trị -> chỉ các app trong list mới được xem thông báo đó
    - Field 'site' trong announcement:
        + Nếu rỗng -> thông báo áp dụng cho TẤT CẢ site (site này được xem)
        + Nếu có giá trị -> chỉ các site trong list mới được xem thông báo đó
    - Field 'status': Không lấy bản ghi có status = 'Hidden'
    
    Args:
        name_app (str): Tên app cần lấy thông báo (bắt buộc, chắc chắn có giá trị)
        site (str): Tên site cần lấy thông báo (bắt buộc)
        arg_email (str): Email của user để xác định team
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "data": list  # Danh sách thông báo marketing mà app được phép xem
        }
    
    Examples:
        GET /api/method/press.api.app_marketing.api.get_marketing_announcements?name_app=mbw_ats&site=demo.mbwcloud.com
    """
    try:
        if not name_app:
            return {
                "success": False,
                "message": "Parameter 'name_app' is required",
                "error_code": "MISSING_NAME_APP"
            }
        
        if not site:
            return {
                "success": False,
                "message": "Parameter 'site' is required",
                "error_code": "MISSING_SITE"
            }
        
        # Validate team access
        validate_team_access(arg_email)
        
        # Lấy tất cả announcements không có status = 'Hidden'
        announcements = frappe.get_all(
            "MBW Announcements Marketing",
            filters=[
                ["status", "!=", "Hidden"]
            ],
            fields=[
                "name",
                "name_announcement",
                "type_announcement",
                "type_show",
                "day_start",
                "day_end",
                "status",
                "priority",
                "content"
            ]
        )
        
        filtered_announcements = []
        
        for announcement in announcements:
            # Lấy child table data cho app và site
            announcement_doc = frappe.get_doc("MBW Announcements Marketing", announcement.name)
            
            # Check app filter: App này có được phép xem thông báo không?
            app_list = [row.app for row in announcement_doc.app] if announcement_doc.app else []
            # Nếu app_list rỗng -> tất cả app đều xem được (bao gồm app này)
            # Nếu app_list có giá trị -> chỉ app trong list mới xem được
            app_match = len(app_list) == 0 or name_app in app_list
            
            # Check site filter
            site_list = [row.site for row in announcement_doc.site] if announcement_doc.site else []
            # Nếu site_list rỗng -> áp dụng cho tất cả site
            # Nếu site_list có giá trị -> chỉ áp dụng cho site trong list
            site_match = len(site_list) == 0 or site in site_list
            
            # Chỉ thêm vào kết quả nếu cả app và site đều match
            if app_match and site_match:
                filtered_announcements.append({
                    "name": announcement.name,
                    "name_announcement": announcement.name_announcement,
                    "type_announcement": announcement.type_announcement,
                    "type_show": announcement.type_show,
                    "day_start": announcement.day_start,
                    "day_end": announcement.day_end,
                    "status": announcement.status,
                    "priority": announcement.priority,
                    "content": announcement.content
                })
        
        return {
            "success": True,
            "message": f"Retrieved {len(filtered_announcements)} marketing announcements",
            "data": filtered_announcements
        }
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), "Authentication Error in get_marketing_announcements")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), "Permission Error in get_marketing_announcements")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_marketing_announcements API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 1000, "window": 3600}
)
def get_latest_announcement_timestamp():
    """
    API siêu nhẹ để lấy timestamp của announcement mới nhất
    Bảo mật bằng API Token
    
    Authentication:
        - Yêu cầu API Key & Secret
        - Rate limit: 1000 requests/hour
    
    Returns:
        dict: {
            "success": bool,
            "timestamp": str,  # MAX(modified) với status='Active'
            "from_cache": bool
        }
    
    Examples:
        GET /api/method/press.api.app_marketing.api.get_latest_announcement_timestamp
        Headers:
            Authorization: token <api_key>:<api_secret>
    """
    try:
        # Check cache first
        cache = frappe.cache()
        from press.utils.cache_utils import ANNOUNCEMENT_TIMESTAMP_KEY
        
        cached_timestamp = cache.get_value(ANNOUNCEMENT_TIMESTAMP_KEY)
        if cached_timestamp:
            return {
                "success": True,
                "timestamp": cached_timestamp,
                "from_cache": True
            }
        
        # Query MAX(modified) - chỉ lấy status='Active'
        result = frappe.db.sql("""
            SELECT MAX(modified) as latest_modified
            FROM `tabMBW Announcements Marketing`
            WHERE status = 'Running'
        """, as_dict=True)
        
        timestamp = str(result[0].latest_modified) if result and result[0].latest_modified else None
        
        # Cache for 5 minutes
        if timestamp:
            cache.set_value(ANNOUNCEMENT_TIMESTAMP_KEY, timestamp, expires_in_sec=300)
        
        return {
            "success": True,
            "timestamp": timestamp,
            "from_cache": False
        }
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), "Authentication Error in get_latest_announcement_timestamp")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), "Permission Error in get_latest_announcement_timestamp")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_latest_announcement_timestamp API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }


@frappe.whitelist()
@validate_api_request(
    required_headers=['User-Agent'],
    api_key_required=True,
    rate_limit={"limit": 1000, "window": 3600}
)
def get_all_announcements():
    """
    API bảo mật để cung cấp dữ liệu announcements
    
    Authentication:
        - Yêu cầu API Key & Secret
        - Rate limit: 1000 requests/hour
    
    Cache:
        - Tự cache ở phía Press để bảo vệ database
        - TTL: 6 giờ (21600s)
        - Auto clear khi có update/delete
    
    Returns:
        dict: {
            "success": bool,
            "data": list,  # Tất cả announcements với full data
            "total": int,  # Tổng số announcements
            "from_cache": bool
        }
    
    Examples:
        GET /api/method/press.api.app_marketing.api.get_all_announcements
        Headers:
            Authorization: token <api_key>:<api_secret>
    """
    try:
        # Check cache first
        cache = frappe.cache()
        from press.utils.cache_utils import ANNOUNCEMENT_CACHE_KEY
        
        cached_data = cache.get_value(ANNOUNCEMENT_CACHE_KEY)
        if cached_data:
            return {
                "success": True,
                "data": cached_data,
                "total": len(cached_data),
                "from_cache": True
            }
        
        # Cache miss - query database
        # Chỉ lấy announcements với status='Running' (Active)
        announcements = frappe.get_all(
            "MBW Announcements Marketing",
            filters=[
                ["status", "=", "Running"]
            ],
            fields=[
                "name",
                "name_announcement",
                "type_announcement",
                "type_show",
                "day_start",
                "day_end",
                "status",
                "priority",
                "content",
                "modified"
            ]
        )
        
        # Lấy child table data cho từng announcement
        full_announcements = []
        for announcement in announcements:
            announcement_doc = frappe.get_doc("MBW Announcements Marketing", announcement.name)
            
            # Get app list
            app_list = [row.app for row in announcement_doc.app] if announcement_doc.app else []
            
            # Get site list
            site_list = [row.site for row in announcement_doc.site] if announcement_doc.site else []
            
            full_announcements.append({
                "name": announcement.name,
                "name_announcement": announcement.name_announcement,
                "type_announcement": announcement.type_announcement,
                "type_show": announcement.type_show,
                "day_start": announcement.day_start,
                "day_end": announcement.day_end,
                "status": announcement.status,
                "priority": announcement.priority,
                "content": announcement.content,
                "modified": announcement.modified,
                "apps": app_list,  # Empty list = áp dụng cho tất cả app
                "sites": site_list  # Empty list = áp dụng cho tất cả site
            })
        
        # Sắp xếp theo priority (cao -> thấp) và day_start (mới -> cũ)
        full_announcements.sort(
            key=lambda x: (-(x.get("priority") or 0), x.get("day_start") or ""),
            reverse=True
        )
        
        # Cache for 6 hours để bảo vệ database
        cache.set_value(ANNOUNCEMENT_CACHE_KEY, full_announcements, expires_in_sec=21600)
        
        return {
            "success": True,
            "data": full_announcements,
            "total": len(full_announcements),
            "from_cache": False
        }
        
    except frappe.AuthenticationError as e:
        frappe.log_error(frappe.get_traceback(), "Authentication Error in get_all_announcements API")
        return {
            "success": False,
            "message": str(e),
            "error_code": "AUTHENTICATION_ERROR"
        }
    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), "Permission Error in get_all_announcements API")
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_all_announcements API")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "error_code": "API_ERROR"
        }
 