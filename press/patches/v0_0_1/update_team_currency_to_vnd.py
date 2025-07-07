import frappe


def execute():
    """Update existing teams to use VND as default currency"""
    
    # Update teams that are not from India or United States to VND
    frappe.db.sql("""
        UPDATE `tabTeam` 
        SET currency = 'VND' 
        WHERE currency = 'USD' 
        AND (country IS NULL OR country NOT IN ('India', 'United States'))
    """)
    
    # Update teams with India country to INR (in case some are wrong)
    frappe.db.sql("""
        UPDATE `tabTeam` 
        SET currency = 'INR' 
        WHERE country = 'India' 
        AND currency != 'INR'
    """)
    
    # Update teams with United States country to USD (this should be correct already)
    frappe.db.sql("""
        UPDATE `tabTeam` 
        SET currency = 'USD' 
        WHERE country = 'United States' 
        AND currency != 'USD'
    """)
    
    # Commit the changes
    frappe.db.commit()
    
    print("Updated team currencies: VND as default, INR for India, USD for United States") 