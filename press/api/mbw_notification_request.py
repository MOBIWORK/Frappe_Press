import frappe
from frappe import _


@frappe.whitelist()
def get_mbw_notification_requests(status=None, type=None, site=None):
	"""Get list of MBW Notification Requests"""
	
	# Check if user has permission to access this data
	if not frappe.has_permission("MBW Notification Request", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	
	# Build filters
	filters = {}
	if status:
		filters["status"] = status
	if type:
		filters["type"] = type
	if site:
		filters["site"] = ["like", f"%{site}%"]
	
	# Get the requests with required fields
	requests = frappe.get_all(
		"MBW Notification Request",
		fields=[
			"name",
			"site",
			"status", 
			"type",
			"creation",
			"description"
		],
		filters=filters,
		order_by="creation desc"
	)
	
	return requests


@frappe.whitelist()
def update_request_status(site, request_type, status="Done"):
	"""Update MBW Notification Request status for a specific site and type"""
	
	# Check if user has permission to access this data
	if not frappe.has_permission("MBW Notification Request", "write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	
	# Find the request with matching site and type that is currently Ongoing
	requests = frappe.get_all(
		"MBW Notification Request",
		filters={
			"site": site,
			"type": request_type,
			"status": "Ongoing"
		},
		fields=["name"]
	)
	
	# Update all matching requests to Done status
	updated_count = 0
	for request in requests:
		doc = frappe.get_doc("MBW Notification Request", request.name)
		doc.status = status
		doc.save()
		updated_count += 1
	
	frappe.db.commit()
	
	return {
		"success": True,
		"updated_count": updated_count,
		"message": f"Updated {updated_count} request(s) for site {site} with type {request_type} to {status}"
	}
