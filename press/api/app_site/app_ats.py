import frappe
from frappe import _
import re
from press.utils import (
    get_current_team,
)
from press.api.app_site import get_domain_setup

PATTERN_DOMAIN = r'^[a-z0-9][a-z0-9-]*[a-z0-9]$'

def check_site_exists(subdomain, domain):
    banned_domains = frappe.get_all(
            "Blocked Domain", {"block_for_all": 1}, pluck="name")
    if banned_domains and subdomain in banned_domains:
        return True
    else:
        return bool(
            frappe.db.exists("Blocked Domain", {
                                "name": subdomain, "root_domain": domain})
            or frappe.db.exists(
                "Site", {"subdomain": subdomain, "domain": domain,
                            "status": ("!=", "Archived")}
            )
        )

def create_site(team, site_name, subdomain, parent_host, lang='vi'):
    if not team:
        team = get_current_team(get_doc=True)

    app_a = 'mbw_ats'
    app_name = 'go1_cms'
    
    linked_app = frappe.get_value("Linked Applications", {'app_a': app_a}, ['plan', 'domain', 'cluster', 'group'], as_dict=1)
    if not linked_app:
        frappe.throw(_("App not integrated", lang))
    
    plan = linked_app.plan
    domain = linked_app.domain
    cluster = linked_app.cluster
    group = linked_app.group
    server = None
    parent_host = parent_host
    
    files = {}
    apps = ['frappe', app_name]
    skip_failing_patches = False
    
    site = frappe.get_doc(
        {
            "doctype": "Site",
            "subdomain": subdomain,
            "domain": domain,
            "group": group,
            "parent_host": parent_host,
            "server": server,
            "cluster": cluster,
            "apps": [{"app": app} for app in apps],
            "team": team.name,
            "free": team.free_account,
            "subscription_plan": plan,
            "remote_config_file": files.get("config"),
            "remote_database_file": files.get("database"),
            "remote_public_file": files.get("public"),
            "remote_private_file": files.get("private"),
            "skip_failing_patches": skip_failing_patches,
        },
    )
    
    # set config
    doc_site_a = frappe.get_value("Site", site_name, ["name", "api_key", "api_secret"], as_dict=1)
    config = {
        'lang': lang,
        f'{app_a}_site_name': 'https://' + site_name,
        "webhook_base_url":'https://' + site_name
    }
    if doc_site_a.api_key:
        config[f'{app_a}_api_key'] = doc_site_a.api_key
    if doc_site_a.api_secret:
        config[f'{app_a}_api_secret'] = doc_site_a.api_secret

    site._update_configuration(config, save=False)
    site.insert(ignore_permissions=True)
    site.create_subscription(plan)
    
    return site


@frappe.whitelist(methods=["POST"])
def create_site_app(**kwargs):
    lang = kwargs.get('lang') or 'vi'
    app_a = 'mbw_ats'
    app_name = 'go1_cms'

    try:
        team = get_current_team(get_doc=True)

        site_name = kwargs.get('site_name')
        subdomain = kwargs.get('subdomain')
        parent_host = kwargs.get('parent_host')
        
        if not site_name:
            frappe.throw(_("Site name is required", lang))
        if not app_name:
            frappe.throw(_("App name is required", lang))
        if not subdomain:
            frappe.throw(_("Subdomain is required", lang))
        
        if not frappe.db.exists("Site", {'team': team.name, 'name': site_name}):
            frappe.throw(_("Site name not found", lang))
        
        if len(subdomain) < 2 or len(subdomain) > 32:
            frappe.throw(_("Subdomain must be between 2 and 32 characters", lang))
        if not re.match(PATTERN_DOMAIN, subdomain):
            frappe.throw(_("Subdomain must be in lowercase and can only contain letters, numbers, and hyphens", lang))
        
        linked_app = frappe.get_value("Linked Applications", {'app_a': app_a}, ['domain', 'group'], as_dict=1)
        if not linked_app:
            frappe.throw(_("App not integrated", lang))
        
        group = linked_app.group
        
        if check_site_exists(subdomain, linked_app.domain):
            frappe.throw(_("Subdomain already exists", lang))

        if not frappe.db.exists("Release Group App", {'parent': group, 'app': app_name}):
            frappe.throw(_("App not installed", lang))
        
        # site_b = f"{subdomain}.{domain}"
        if frappe.db.exists("App Integration Settings", {"site_a": site_name, "app_a": app_a, "app_b": app_name}):
            frappe.throw(_("Cannot recreate again", lang))
        
        site = create_site(team=team, site_name=site_name, subdomain=subdomain, parent_host=parent_host, lang=lang)
        
        doc_site_a = frappe.get_value("Site", site_name, ["name", "api_key", "api_secret"], as_dict=1)
        # add app integration
        app_integration = frappe.new_doc("App Integration Settings")
        app_integration.site_a = site_name
        app_integration.app_a = app_a
        app_integration.api_key_a = doc_site_a.api_key
        app_integration.api_secret_a = doc_site_a.api_secret
        app_integration.site_b = site.name
        app_integration.app_b = app_name
        app_integration.webhook_base_url = site_name
        app_integration.save(ignore_permissions=True)
        
        frappe.db.commit()

        return {
            "site": site.name,
        }
    except frappe.ValidationError as e:
        frappe.clear_last_message()
        frappe.db.rollback()
        frappe.throw(_(str(e), lang))
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Site App From Site ATS Error")
        frappe.throw(_("Error", lang))


@frappe.whitelist(methods=["POST"])
def recreate_site_app(**kwargs):
    lang = kwargs.get('lang') or 'vi'
    app_a = 'mbw_ats'
    app_name = 'go1_cms'
    site_name = kwargs.get('site_name')
    
    try:        
        app_inte = frappe.get_value("App Integration Settings", {"site_a": site_name, "app_a": app_a, "app_b": app_name, "webhook_base_url": site_name}, ['name', 'site_b', 'reinstall'], as_dict=1)
        if not app_inte:
            frappe.throw(_("App not integrated", lang))

        if app_inte.reinstall:
            frappe.throw(_("Cannot recreate again", lang))
        
        site = frappe.get_doc("Site", app_inte.site_b)
        if site.status != "Broken":
            frappe.throw(_("Cannot recreate site", lang))

        site.archive()
        
        frappe.db.set_value("App Integration Settings", app_inte.name, {
            'reinstall': 1
        })        
        frappe.db.commit()
        
        return {
            "site": site.name,
        }
    except frappe.ValidationError as e:
        frappe.clear_last_message()
        frappe.db.rollback()
        frappe.throw(_(str(e), lang))
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Site App From Site ATS Error")
        frappe.throw(_("Error", lang))

@frappe.whitelist(methods=["POST"])
def get_domain(**kwargs):
    app_a = 'mbw_ats'
    domain = get_domain_setup(app_a)
    
    return {
        "domain": domain,
    }
