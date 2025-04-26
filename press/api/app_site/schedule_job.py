import frappe

def auto_configure_app_site():
    try:
        app_integrations = frappe.get_all("App Integration Settings", filters={"configured": 0}, fields=["name", "site_a", "app_a", "api_key_a", "site_b", "api_key_b"])
        site_config = {}
        
        for integration in app_integrations:
            site_a = frappe.get_value("Site", integration.site_a, ["name", "api_key", "api_secret"], as_dict=1)
            site_b = frappe.get_value("Site", integration.site_b, ["name", "status"], as_dict=1)
            if not site_a or not site_a.api_key:
                continue
            if not site_b or site_b.status not in ["Active","Suspended"]:
                continue
            
            if not integration.api_key_a:
                config = site_config.get(integration.site_b) or {}
                config[f'{integration.app_a}_site_name'] = 'https://' + site_a.name
                config[f'{integration.app_a}_api_key'] = site_a.api_key
                config[f'{integration.app_a}_api_secret'] = site_a.api_secret
                site_config[integration.site_b] = config
                
                data_update = {
                    'api_key_a': site_a.api_key,
                    'api_secret_a': site_a.api_secret,
                }
                if integration.api_key_b:
                    data_update['configured'] = 1
                frappe.db.set_value('App Integration Settings', integration.name, data_update)

        for site, config in site_config.items():
            site_doc = frappe.get_doc("Site", site)
            site_doc.update_site_config(config)
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Configure App Site Error")