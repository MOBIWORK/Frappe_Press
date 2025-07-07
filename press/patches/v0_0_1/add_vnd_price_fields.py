import frappe


def execute():
	"""Add price_vnd fields to plan doctypes"""
	
	# Add price_vnd column to Site Plan
	if not frappe.db.has_column("Site Plan", "price_vnd"):
		frappe.db.sql("""
			ALTER TABLE `tabSite Plan` 
			ADD COLUMN `price_vnd` decimal(21,9) DEFAULT 0.0
		""")
		
	# Add price_vnd column to Server Plan
	if not frappe.db.has_column("Server Plan", "price_vnd"):
		frappe.db.sql("""
			ALTER TABLE `tabServer Plan` 
			ADD COLUMN `price_vnd` decimal(21,9) DEFAULT 0.0
		""")
		
	# Add price_vnd column to Server Storage Plan
	if not frappe.db.has_column("Server Storage Plan", "price_vnd"):
		frappe.db.sql("""
			ALTER TABLE `tabServer Storage Plan` 
			ADD COLUMN `price_vnd` decimal(21,9) DEFAULT 0.0
		""")
		
	# Add price_vnd column to Cluster Plan
	if not frappe.db.has_column("Cluster Plan", "price_vnd"):
		frappe.db.sql("""
			ALTER TABLE `tabCluster Plan` 
			ADD COLUMN `price_vnd` decimal(21,9) DEFAULT 0.0
		""")
	
	# Update existing plans with VND prices (1 USD = 25,000 VND estimate)
	frappe.db.sql("""
		UPDATE `tabSite Plan` 
		SET `price_vnd` = `price_usd` * 25000 
		WHERE (`price_vnd` IS NULL OR `price_vnd` = 0) 
		AND `price_usd` > 0 AND `enabled` = 1
	""")
	
	frappe.db.sql("""
		UPDATE `tabServer Plan` 
		SET `price_vnd` = `price_usd` * 25000 
		WHERE (`price_vnd` IS NULL OR `price_vnd` = 0) 
		AND `price_usd` > 0 AND `enabled` = 1
	""")
	
	frappe.db.sql("""
		UPDATE `tabServer Storage Plan` 
		SET `price_vnd` = `price_usd` * 25000 
		WHERE (`price_vnd` IS NULL OR `price_vnd` = 0) 
		AND `price_usd` > 0 AND `enabled` = 1
	""")
	
	# Update Marketplace App Plans if needed
	frappe.db.sql("""
		UPDATE `tabMarketplace App Plan` 
		SET `price_vnd` = `price_usd` * 25000 
		WHERE (`price_vnd` IS NULL OR `price_vnd` = 0) 
		AND `price_usd` > 0 AND `enabled` = 1
	""")
	
	# Update Cluster Plans
	frappe.db.sql("""
		UPDATE `tabCluster Plan` 
		SET `price_vnd` = `price_usd` * 25000 
		WHERE (`price_vnd` IS NULL OR `price_vnd` = 0) 
		AND `price_usd` > 0 AND `enabled` = 1
	""")
	
	frappe.db.commit()
	print("✓ Added price_vnd fields and updated VND prices for all plan types") 