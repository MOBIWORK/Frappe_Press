import frappe
from frappe import _
from typing import List, Dict, Optional


@frappe.whitelist(allow_guest=True)
def get_eligible_vouchers(product: str, utm_source: Optional[str] = None, utm_campaign: Optional[str] = None) -> List[Dict]:
	"""
	Get eligible vouchers based on product, utm_source and utm_campaign.
	Returns voucher information for display on signup page.
	"""
	try:
		if not product:
			return []
		
		filters = {
			"status": "Active",
			"day_start": ["<=", frappe.utils.today()],
		}
		vouchers = frappe.get_all(
			"MBW Voucher",
			filters=filters,
			fields=["name", "code_voucher", "name_voucher", "deducted_amount", 
					"day_end", "expiry_voucher", "max_number_voucher", 
					"issued_number_voucher", "description"],
			order_by="deducted_amount desc"
		)
		
		if not vouchers:
			return []
		
		eligible_vouchers = []
		today = frappe.utils.getdate(frappe.utils.today())
		
		for voucher in vouchers:
			day_end_date = frappe.utils.getdate(voucher.day_end) if voucher.day_end else None
			if day_end_date and day_end_date < today:
				continue
			
			if voucher.max_number_voucher > 0 and voucher.issued_number_voucher >= voucher.max_number_voucher:
				continue
			
			if not _check_app_eligibility(voucher.name, product):
				continue
			
			if utm_source and not _check_source_eligibility(voucher.name, utm_source, "MBW Voucher Lead Source", "lead_source"):
				continue
			
			if utm_campaign and not _check_source_eligibility(voucher.name, utm_campaign, "MBW Voucher Campaign Source", "campaign_source"):
				continue
			
			expiry_date = None
			if voucher.day_end:
				expiry_date = voucher.day_end
			elif voucher.expiry_voucher:
				expiry_date = frappe.utils.add_days(frappe.utils.today(), int(voucher.expiry_voucher))
		
			eligible_vouchers.append({
				"code": voucher.code_voucher,
				"name": voucher.name_voucher,
				"amount": voucher.deducted_amount or 0,
				"expiry_date": expiry_date,
				"description": voucher.description
			})
	
		return eligible_vouchers
		
	except Exception as e:
		frappe.log_error(f"Error in get_eligible_vouchers: {str(e)}")
		return []


def _check_app_eligibility(voucher_name: str, product: str) -> bool:
	"""Check if voucher is eligible for the given app"""
	apps = frappe.get_all(
		"MBW Voucher App",
		filters={"parent": voucher_name},
		fields=["app"],
		limit=1
	)
	
	if not apps:
		return True

	app_list = frappe.get_all(
		"MBW Voucher App",
		filters={"parent": voucher_name, "app": product},
		limit=1
	)
	
	result = bool(app_list)
	return result


def _check_source_eligibility(voucher_name: str, source_value: str, child_doctype: str, field_name: str) -> bool:
	"""Check if voucher is eligible for the given source"""
	sources = frappe.get_all(
		child_doctype,
		filters={"parent": voucher_name},
		fields=[field_name],
		limit=1
	)
	
	if not sources:
		return True
	
	matching_sources = frappe.get_all(
		child_doctype,
		filters={"parent": voucher_name, field_name: source_value},
		limit=1
	)
	
	result = bool(matching_sources)
	return result


@frappe.whitelist()
def validate_and_apply_vouchers(team: str, product: str, utm_source: Optional[str] = None, utm_campaign: Optional[str] = None) -> Dict:
	"""
	Validate vouchers and apply them to the team.
	Called when user creates account in SetupAccount page.
	
	Args:
		team: Can be either team ID or user email
	"""
	try:
		# Check if team is an ID or email
		team_id = team
		if not frappe.db.exists("Team", team):
			team_name = frappe.db.get_value("Team", {"user": team}, "name")
			if team_name:
				team_id = team_name
			else:
				return {"success": False, "message": _("Team not found")}
		
		eligible_vouchers = get_eligible_vouchers(product, utm_source, utm_campaign)
		
		if not eligible_vouchers:
			return {"success": True, "message": _("No eligible vouchers"), "applied_count": 0}
		
		applied_count = 0
		team_doc = frappe.get_doc("Team", team_id)
		today = frappe.utils.getdate(frappe.utils.today())
		
		for voucher_info in eligible_vouchers:
			voucher_data = frappe.db.sql("""
				SELECT name, code_voucher, deducted_amount, type_voucher, status,
					   day_end, max_number_voucher, issued_number_voucher
				FROM `tabMBW Voucher`
				WHERE code_voucher = %s
				FOR UPDATE
			""", (voucher_info["code"],), as_dict=True)
			
			if not voucher_data:
				continue
	
			voucher_data = voucher_data[0]

			if voucher_data.status != "Active":
				continue
		
			day_end_date = frappe.utils.getdate(voucher_data.day_end) if voucher_data.day_end else None
			if day_end_date and day_end_date < today:
				continue
	
			if voucher_data.max_number_voucher > 0 and voucher_data.issued_number_voucher >= voucher_data.max_number_voucher:
				continue
			

			existing_claim = frappe.get_all(
				"MBW Voucher Claim",
				filters={
					"parent": team_id,
					"voucher_id": voucher_data.name
				},
				limit=1
			)
			
			if existing_claim:
				continue
	
			team_doc.append("vouchers", {
				"voucher_id": voucher_data.name,
				"amount_used": 0,
				"deducted_amount": voucher_data.deducted_amount,
				"type_voucher": voucher_data.type_voucher,
				"status": "Active",
				"usage_status": "Unused"
			})
	
			frappe.db.sql("""
				UPDATE `tabMBW Voucher`
				SET issued_number_voucher = issued_number_voucher + 1,
					modified = NOW()
				WHERE name = %s
			""", (voucher_data.name,))
	
			applied_count += 1

		if applied_count > 0:
			team_doc.save(ignore_permissions=True)
			frappe.db.commit()
	
		return {
			"success": True,
			"message": _("Vouchers applied successfully"),
			"applied_count": applied_count
		}
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Error in validate_and_apply_vouchers: {str(e)}", "Voucher Application Error")
		return {"success": False, "message": _("Failed to apply vouchers")}


def _validate_voucher_for_application(voucher) -> bool:
	"""Final validation before applying voucher"""
	if voucher.status != "Active":
		return False
	
	if voucher.day_end and voucher.day_end < frappe.utils.today():
		return False
	
	if voucher.max_number_voucher > 0 and voucher.issued_number_voucher >= voucher.max_number_voucher:
		return False
	
	return True
