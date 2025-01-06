import frappe

def after_insert_and_update_market_app(doc, method=None):
    marketplace_app_plan = doc.marketplace_app_plan
    if marketplace_app_plan is not None and doc.app == 'roadai':
        marketplace_app_plan_doc = frappe.get_doc('Marketplace App Plan', marketplace_app_plan)
        site_doc = frappe.get_doc('Site', doc.site)
        features = marketplace_app_plan_doc.Features
        for feature in features:
            label_field = feature.label_field
            value_field = feature.value_field
            if label_field == "max_storage_roadai":
                existing_config = next((conf for conf in site_doc.configuration if conf.key == "max_storage_roadai"), None)
                if existing_config:
                    existing_config.value = value_field or 5
                else:
                    site_doc.append('configuration', {
                        "key": "max_storage_roadai",
                        "value": value_field or 5,
                        "type": "Number"
                    })
            if label_field == "max_pupv_roadai":
                existing_config = next((conf for conf in site_doc.configuration if conf.key == "max_pupv_roadai"), None)
                if existing_config:
                    existing_config.value = value_field or 500
                else:
                    site_doc.append('configuration', {
                        "key": "max_pupv_roadai",
                        "value": value_field or 500,
                        "type": "Number"
                    })
        site_doc.save()
        frappe.db.commit()

            

