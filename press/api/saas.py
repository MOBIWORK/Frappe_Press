import frappe
from frappe import _
import json
from frappe.core.utils import find
from frappe.core.doctype.user.user import test_password_strength
from frappe.utils.password import get_decrypted_password
from press.press.doctype.team.team import Team
from press.api.account import get_account_request_from_key
from press.utils import get_current_team, group_children_in_result, log_error

from press.press.doctype.site.saas_site import (
    SaasSite,
    get_default_team_for_app,
    get_saas_domain,
    get_saas_site_plan,
    get_saas_group,
    get_saas_cluster,
    get_saas_apps,
    set_site_in_subscription_docs,
)
from press.api.site import (
    _new
)
from press.api.account import (
    update_billing_information
)
from press.press.doctype.site.saas_pool import get as get_pooled_saas_site
from press.press.doctype.site.erpnext_site import get_erpnext_domain
from press.utils.telemetry import capture, identify


# ----------------------------- SIGNUP APIs ---------------------------------


@frappe.whitelist(allow_guest=True)
def account_request(
        subdomain,
        email,
        password,
        first_name,
        app,
        country="Vietnam",
        phone_number='',
        last_name='',
        url_args=None,
):
    """
    return: Stripe setup intent and AR key if stripe flow, else None
    """
    url_args = json.loads(url_args) if url_args else {}
    lang = url_args.get('lang', 'vi')
    email = email.strip().lower()
    frappe.utils.validate_email_address(email, True)
    frappe.throw(_('Account with email {0} has been deactivated', lang).format(email))

    exists, enabled = frappe.db.get_value("Team", {"user": email}, ["name", "enabled"]
    ) or [0, 0]

    if exists and not enabled:
        frappe.throw(_('Account with email {0} has been deactivated', lang).format(email))
    elif exists and enabled:
        frappe.throw(_('Account with email {0} is already registered', lang).format(email))

    if not check_subdomain_availability(subdomain, app):
        frappe.throw(_('Subdomain {0} is already taken', lang).format(subdomain))

    password_validation = validate_password(
        password, first_name, last_name, email)
    if not password_validation.get("validation_passed"):
        frappe.throw(password_validation.get("suggestion")[0])

    all_countries = frappe.db.get_all("Country", pluck="name")
    country = find(all_countries, lambda x: x.lower() == country.lower())
    if not country:
        frappe.throw(_("Country field should be a valid country name", lang))

    current_user = frappe.session.user
    try:
        frappe.set_user("Administrator")
        account_request = frappe.get_doc(
            {
                "doctype": "Account Request",
                "saas": True,
                "saas_app": app,
                "erpnext": False,
                "subdomain": subdomain,
                "email": email,
                "password": password,
                "role": "Press Admin",
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "country": country,
                "url_args": url_args or json.dumps({}),
                "send_email": True,
                "language": lang
            }
        )
        site_name = account_request.get_site_name()
        identify(
            site_name,
            app=account_request.saas_app,
            source=json.loads(url_args).get("source") if url_args else "fc",
        )
        account_request.insert(ignore_permissions=True)
        capture("completed_server_account_request", "fc_saas", site_name)
    except Exception as e:
        log_error("Account Request Creation Failed", data=e)
        raise
    finally:
        frappe.set_user(current_user)

    # create_or_rename_saas_site(app, account_request)

# === saas old
# def create_or_rename_saas_site(app, account_request):
#     """
#     Creates site for Saas App. These are differentiated by `standby_for` field in site doc
#     """
#     current_user = frappe.session.user
#     current_session_data = frappe.session.data
#     frappe.set_user("Administrator")

#     try:
#         enable_hybrid_pools = frappe.db.get_value(
#             "Saas Settings", app, "enable_hybrid_pools")
#         hybrid_saas_pool = (
#             get_hybrid_saas_pool(
#                 account_request) if enable_hybrid_pools else ""
#         )

#         pooled_site = get_pooled_saas_site(app, hybrid_saas_pool)
#         if pooled_site:
#             SaasSite(site=pooled_site, app=app).rename_pooled_site(
#                 account_request)
#         else:
#             saas_site = SaasSite(
#                 account_request=account_request, app=app, hybrid_saas_pool=hybrid_saas_pool
#             ).insert(ignore_permissions=True)
#             set_site_in_subscription_docs(
#                 saas_site.subscription_docs, saas_site.name)
#             saas_site.create_subscription(get_saas_site_plan(app))

#         capture("completed_server_site_created",
#                 "fc_saas", account_request.get_site_name())
#     except Exception as e:
#         log_error("Saas Site Creation or Rename failed", data=e)

#     finally:
#         frappe.set_user(current_user)
#         frappe.session.data = current_session_data


# === saas mbw
def create_or_rename_saas_site(app, account_request):
    """
    Creates site for Saas App
    """
    try:
        site = {
            "domain": get_saas_domain(app),
            "name": account_request.subdomain,
            "apps": get_saas_apps(app),
            "group": get_saas_group(app),
            "cluster": get_saas_cluster(app),
            "plan": get_saas_site_plan(app)
        }
        _new(site)
        
        capture("completed_server_site_created",
                "fc_saas", account_request.get_site_name())
    except Exception as e:
        log_error("Saas Site Creation or Rename failed", data=e)


@frappe.whitelist()
def new_saas_site(subdomain, app):
    frappe.only_for("System Manager")

    pooled_site = get_pooled_saas_site(app)
    if pooled_site:
        site = SaasSite(site=pooled_site, app=app).rename_pooled_site(
            subdomain=subdomain)
    else:
        site = SaasSite(app=app, subdomain=subdomain).insert(
            ignore_permissions=True)
        site.create_subscription(get_saas_site_plan(app))

    site.reload()
    site.team = get_default_team_for_app(app)
    site.save(ignore_permissions=True)

    frappe.db.commit()

    return site


@frappe.whitelist()
def get_saas_site_status(site):
    if frappe.db.exists("Site", site):
        return {"site": site, "status": frappe.db.get_value("Site", site, "status")}

    return {"site": site, "status": "Pending"}


def get_hybrid_saas_pool(account_request):
    """
    1. Get all hybrid pools and their rules
    2. Filter based on rules and return Hybrid pool
    3. Returns the first rule match
    return: The hybrid pool name that site belongs to based on the Account Request
    conditions
    """
    hybrid_pool = ""
    all_pools = frappe.get_all(
        "Hybrid Saas Pool", {"app": account_request.saas_app}, pluck="name"
    )
    ar_rules = frappe.get_all(
        "Account Request Rules",
        {"parent": ("in", all_pools)},
        ["parent", "field", "condition", "value"],
        group_by="parent",
    )

    for rule in ar_rules:
        if eval(f"account_request.{rule.field} {rule.condition} '{rule.value}'"):
            hybrid_pool = rule.parent
            return hybrid_pool

    return hybrid_pool


@frappe.whitelist(allow_guest=True)
def validate_password(password, first_name, last_name, email):
    passed = True
    suggestion = None

    user_data = (first_name, last_name, email)
    result = test_password_strength(password, "", None, user_data)
    feedback = result.get("feedback", None)

    if feedback and not feedback.get("password_policy_validation_passed", False):
        passed = False
        suggestion = feedback.get("suggestions") or [
            "Your password is too weak, please pick a stronger password by adding more words."
        ]

    return {"validation_passed": passed, "suggestion": suggestion}


@frappe.whitelist(allow_guest=True)
def check_subdomain_availability(subdomain, app):
    """
    Checks if subdomain is available to create a new site
    """
    # Only for ERPNext domains

    if len(subdomain) < 4:
        return False

    banned_domains = frappe.get_all(
        "Blocked Domain", {"block_for_all": 1}, pluck="name")
    if banned_domains and subdomain in banned_domains:
        return False

    exists = bool(
        frappe.db.exists(
            "Blocked Domain", {"name": subdomain,
                               "root_domain": get_erpnext_domain()}
        )
        or frappe.db.exists(
            "Site",
            {
                "subdomain": subdomain,
                "domain": get_saas_domain(app),
                "status": ("!=", "Archived"),
            },
        )
    )
    if exists:
        return False

    return True


@frappe.whitelist(allow_guest=True)
def validate_account_request(key, lang='vi'):
    if not key:
        frappe.throw(_("Request Key not provided", lang))
    
    account_request = get_account_request_from_key(key, lang)
    if not account_request:
        frappe.throw(_("Invalid or Expired Key", lang))

    app = frappe.db.get_value(
        "Account Request", {"request_key": key}, "saas_app")
    headless, route = frappe.db.get_value(
        "Saas Setup Account Generator", app, ["headless", "route"]
    )

    if headless:
        headless_setup_account(key)
    else:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/{route}?key={key}&lang={lang}"

    

@frappe.whitelist(allow_guest=True)
def setup_account(key, business_data=None, lang='vi'):
    """
    Includes the data collection step in setup-account.html
    """
    account_request = get_account_request_from_key(key, lang)
    if not account_request:
        frappe.throw(_("Invalid or Expired Key", lang))

    capture(
        "init_server_setup_account",
        "fc_saas",
        account_request.get_site_name(),
    )
    frappe.set_user("Administrator")

    if business_data:
        business_data = frappe.parse_json(business_data)

    account_request.update(business_data)
    account_request.save(ignore_permissions=True)

    create_marketplace_subscription(account_request, business_data)
    capture(
        "completed_server_setup_account",
        "fc_saas",
        account_request.get_site_name(),
    )


@frappe.whitelist(allow_guest=True)
def headless_setup_account(key):
    """
    Ignores the data collection step in setup-account.html
    """
    account_request = get_account_request_from_key(key)
    lang = account_request.language or 'vi'
    if not account_request:
        frappe.throw(_("Invalid or Expired Key", lang))

    capture(
        "init_server_setup_account",
        "fc_saas",
        account_request.get_site_name(),
    )
    frappe.set_user("Administrator")

    create_marketplace_subscription(account_request)
    # create team and enable the subscriptions for site
    capture(
        "completed_server_setup_account",
        "fc_saas",
        account_request.get_site_name(),
    )

    frappe.local.response["type"] = "redirect"
    frappe.local.response[
        "location"
    ] = f"/prepare-site?key={key}&app={account_request.saas_app}&lang={lang}"


# === saas old
# def create_marketplace_subscription(account_request):
#     """
#     Create team, subscription for site and Saas Subscription
#     """
#     team_doc = create_team(account_request)
#     site_name = frappe.db.get_value(
#         "Site", {"account_request": account_request.name})
#     if site_name:
#         frappe.db.set_value("Site", site_name, "team", team_doc.name)

#     subscription = frappe.db.exists(
#         "Subscription", {"document_name": site_name})
#     if subscription:
#         frappe.db.set_value("Subscription", subscription,
#                             "team", team_doc.name)

#     marketplace_subscriptions = frappe.get_all(
#         "Marketplace App Subscription",
#         {"site": site_name, "status": "Disabled"},
#         pluck="name",
#     )
#     for subscription in marketplace_subscriptions:
#         frappe.db.set_value(
#             "Marketplace App Subscription",
#             subscription,
#             {"status": "Active", "team": team_doc.name},
#         )

#     frappe.set_user(team_doc.user)
#     frappe.local.login_manager.login_as(team_doc.user)

#     # # config api_key
#     # if site_name:
#     #     site = frappe.get_doc('Site', site_name)
#     #     site.update_site_config()
    
#     # # allocate free credit amount
#     # if team_doc:
#     #     team = frappe.get_doc('Team', team_doc.name)
#     #     team.create_payment_method(
#     #         '', set_default=True
#     #     )
    
#     return site_name

def create_marketplace_subscription(account_request, business_data=None):
    try:
        """
        Create team, subscription for site and Saas Subscription
        """
        team_doc = create_team(account_request)
        
        if isinstance(business_data, dict):
            billing_info = {
                "billing_name": business_data.get('billing_name', ""),
                "address": business_data.get('address', ""),
                "state": business_data.get('province', ""),
                "county": business_data.get('district', ""),
                "tax_code": business_data.get('tax_code', ""),
                "email_id": business_data.get('email_id', ""),
                "phone": business_data.get('phone', ""),
                "enterprise": business_data.get('enterprise', "Cá nhân"),
                "postal_code": "",
                "gstin": "",
                "number_of_employees": 0,
                "areas_of_concern": "",
                "country": "Vietnam"
            }
            billing_details = frappe._dict(billing_info)
            team_doc.update_billing_details(billing_details)

        # allocate free credit amount
        team_doc.reload()
        team_doc.allocate_free_credits()
        team_doc.reload()
        
        # login user
        frappe.set_user(team_doc.user)
        frappe.local.login_manager.login_as(team_doc.user)
        
        # create site
        create_or_rename_saas_site(account_request.saas_app, account_request)
            
        return ''
    except Exception as ex:
        log_error("Create marketplace subscription", data=ex)


def create_team(account_request, get_stripe_id=False):
    """
    Create team and return doc
    """
    email = account_request.email

    if not frappe.db.exists("Team", {"user": email}):
        team_doc = Team.create_new(
            account_request=account_request,
            first_name=account_request.first_name,
            phone=account_request.phone_number,
            password=get_decrypted_password(
                "Account Request", account_request.name, "password"),
            country=account_request.country,
            # is_us_eu=account_request.is_us_eu,
            # via_erpnext=True,
            user_exists=frappe.db.exists("User", email),
        )
    else:
        team_doc = frappe.get_doc("Team", {"user": email})

    if get_stripe_id:
        return team_doc.stripe_customer_id

    return team_doc


@frappe.whitelist(allow_guest=True)
def get_site_status(key, app=None):
    """
    return: Site status
    """
    account_request = get_account_request_from_key(key)
    if not account_request:
        frappe.throw(_("Invalid or Expired Key", 'vi'))

    domain = get_saas_domain(app) if app else get_erpnext_domain()

    site = frappe.db.get_value(
        "Site",
        {"subdomain": account_request.subdomain,
         "domain": domain, "status": "Active"},
        ["status", "subdomain", "name"],
        as_dict=1,
    )
    if site:
        capture("completed_site_allocation", "fc_saas", site.name)
        return site
    else:
        return {"status": "Pending"}


@frappe.whitelist(allow_guest=True)
def get_site_url_and_sid(key, app=None):
    """
    return: Site url and session id for login-redirect
    """
    account_request = get_account_request_from_key(key)
    if not account_request:
        frappe.throw(_("Invalid or Expired Key", 'vi'))

    domain = get_saas_domain(app) if app else get_erpnext_domain()

    name = frappe.db.get_value(
        "Site", {"subdomain": account_request.subdomain, "domain": domain}
    )
    site = frappe.get_doc("Site", name)
    return {
        "url": f"https://{site.name}",
        "sid": site.login(),
    }


@frappe.whitelist()
def get_saas_product_info(product=None):
    team = get_current_team()
    product = frappe.utils.cstr(product)
    site_request = frappe.db.get_value(
        "SaaS Product Site Request",
        filters={
            "saas_product": product,
            "team": team,
            "status": ("in", ["Pending", "Wait for Site"]),
        },
        fieldname=["name", "status", "site"],
        as_dict=1,
    )
    if site_request:
        saas_product = frappe.db.get_value(
            "SaaS Product", {"name": product}, ["name", "title", "logo", "domain"], as_dict=True
        )
        return {
            "title": saas_product.title,
            "logo": saas_product.logo,
            "domain": saas_product.domain,
            "site_request": site_request,
        }


@frappe.whitelist()
def create_site(subdomain, site_request):
    site_request_doc = frappe.get_doc(
        "SaaS Product Site Request", site_request)
    return site_request_doc.create_site(subdomain)


@frappe.whitelist()
def get_site_progress(site_request):
    site_request_doc = frappe.get_doc(
        "SaaS Product Site Request", site_request)
    return site_request_doc.get_progress()


@frappe.whitelist()
def login_to_site(site_request):
    from press.api.site import login

    site_request_doc = frappe.get_doc(
        "SaaS Product Site Request", site_request)
    return login(site_request_doc.site)


@frappe.whitelist()
def subscription(site):
    team = get_current_team()
    if not frappe.db.exists("Site", {"team": team, "name": site}):
        frappe.throw("Invalid Site")

    plans = frappe.db.get_all(
        "Plan",
        fields=[
            "name",
            "plan_title",
            "price_vnd",
            "price_usd",
            "price_inr",
            "cpu_time_per_day",
            "max_storage_usage",
            "max_database_usage",
            "database_access",
            "`tabHas Role`.role",
        ],
        filters={"enabled": True, "document_type": "Site"},
        order_by="price_vnd asc",
    )
    plans = group_children_in_result(plans, {"role": "roles"})

    release_group_name = frappe.db.get_value("Site", site, "group")
    release_group = frappe.get_doc("Release Group", release_group_name)
    is_private_bench = release_group.team == team and not release_group.public
    is_system_user = frappe.session.data.user_type == "System User"
    is_paywalled_bench = is_private_bench and not is_system_user

    filtered_plans = []
    for plan in plans:
        if is_paywalled_bench and plan.price_vnd < 25:
            continue
        if frappe.utils.has_common(plan["roles"], frappe.get_roles()):
            plan.pop("roles", "")
            filtered_plans.append(plan)

    trial_end_date, current_plan = frappe.db.get_value(
        "Site", site, ["trial_end_date", "plan"]
    )
    return {
        "trial_end_date": trial_end_date,
        "current_plan": current_plan,
        "plans": filtered_plans,
    }


@frappe.whitelist()
def set_subscription_plan(site, plan):
    team = get_current_team()
    if not frappe.db.exists("Site", {"team": team, "name": site}):
        frappe.throw("Invalid Site")

    site_doc = frappe.get_doc("Site", site)
    if not site_doc.plan:
        site_doc.create_subscription(plan)
    else:
        site_doc.change_plan(plan)
