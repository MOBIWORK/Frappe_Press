# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
import math


def get_context(context):
    # TODO: Caching, Pagination, Filtering, Sorting
    args = frappe.request.args
    pageCurren = args.get('page') if args.get(
        'page') and int(args.get('page')) > 1 else '1'
    pageSize = args.get('page_size') if args.get(
        'page_size') and int(args.get('page_size')) > 1 else '18'
    skipRow = str(int(pageSize) * (int(pageCurren)-1))
    category = args.get('category', '')
    text_search = args.get('text_search', '')
    context.text_search = text_search
    context.category = category

    context.no_cache = 1
    str_query = """
        SELECT
            COUNT(*) AS total_apps
        FROM
            `tabMarketplace App` marketplace
    """

    if category:
        str_query += """
            INNER JOIN
            `tabMarketplace App Categories` categories
            ON
                categories.parent = marketplace.name
        """

    str_query += """
        WHERE
            marketplace.status = "Published"
    """

    if text_search:
        str_query += f"""
        AND
            marketplace.name LIKE '%{text_search}%'
        """
    if category:
        str_query += f"""
        AND
            categories.category = '{category}'
        """
    str_query += """;"""

    total_all_published_apps = frappe.db.sql(str_query,
                                             as_dict=True,
                                             )[0].get('total_apps')

    if pageSize:
        totalPage = math.ceil(total_all_published_apps/int(pageSize))
    else:
        totalPage = 0

    context.pagination = {
        "total_page": totalPage,
        "page_curren": int(pageCurren),
        "page_size": int(pageSize),
    }

    str_query = """
    SELECT
            marketplace.name,
            marketplace.title,
            marketplace.image,
            marketplace.route,
            marketplace.description,
            COUNT(*) AS total_installs
        FROM
            `tabMarketplace App` marketplace
        LEFT JOIN
            `tabSite App` site
        ON
            site.app = marketplace.app
    """

    if category:
        str_query += """
            INNER JOIN
            `tabMarketplace App Categories` categories
            ON
                categories.parent = marketplace.name
        """

    str_query += """
        WHERE
            marketplace.status = "Published"
    """

    if text_search:
        str_query += f"""
        AND
            marketplace.name LIKE '%{text_search}%'
        """

    if category:
        str_query += f"""
        AND
            categories.category = '{category}'
        """

    str_query += f"""
        GROUP BY
            marketplace.name
        ORDER BY
            total_installs DESC
        OFFSET {skipRow} ROWS
          FETCH NEXT {pageSize} ROWS ONLY;
    """
    all_published_apps = frappe.db.sql(
        str_query,
        as_dict=True,
    )

    context.apps = all_published_apps
    for app in all_published_apps:
        app["categories"] = frappe.db.get_all(
            "Marketplace App Categories", {"parent": app["name"]}, pluck="category"
        )

    context.categories = sorted(
        frappe.db.get_all("Marketplace App Categories",
                          pluck="category", distinct=True)
    )
    if "Featured" in context.categories:
        context.categories.remove("Featured")
        context.categories.insert(0, "Featured")

    featured_apps = frappe.get_all(
        "Featured App",
        filters={"parent": "Marketplace Settings"},
        pluck="app",
        order_by="idx",
    )

    context.featured_apps = sorted(
        filter(lambda x: x.name in featured_apps, all_published_apps),
        key=lambda y: featured_apps.index(y.name),
    )

    context.metatags = {
        "title": "Frappe Cloud Marketplace",
        "description": "One Click Apps for your Frappe Sites",
        "og:type": "website",
    }
