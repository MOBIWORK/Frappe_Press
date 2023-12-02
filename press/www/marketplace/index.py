# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
import math


def generate_pagination(current_page, total_pages):
    visible_pages = 3  # Số lượng trang muốn hiển thị

    # Tính toán khoảng trang cần hiển thị
    start_page = max(1, current_page - (visible_pages // 2))
    end_page = min(total_pages, start_page + visible_pages - 1)

    # Đảm bảo có đủ số trang hiển thị
    if end_page - start_page + 1 < visible_pages:
        start_page = max(1, end_page - visible_pages + 1)

    # Tạo danh sách chứa các trang cần hiển thị
    pagination_list = list(range(start_page, end_page + 1))
    if 1 not in pagination_list and 2 not in pagination_list:
        pagination_list = [1, "..."] + pagination_list
    elif 1 not in pagination_list:
        pagination_list.insert(0, 1)

    if total_pages not in pagination_list and total_pages-1 not in pagination_list:
        pagination_list = pagination_list + ["...", total_pages]
    elif total_pages not in pagination_list:
        pagination_list.extend([total_pages])

    return pagination_list


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

    pagination_list = generate_pagination(int(pageCurren), totalPage)

    context.pagination = {
        "total_page": totalPage,
        "page_curren": int(pageCurren),
        "page_size": int(pageSize),
        "pagination_list": pagination_list
    }

    # totalPage = 10
    # pageCurren = 5
    # pagination_list = generate_pagination(pageCurren, totalPage)
    # print(pagination_list)
    # context.pagination = {
    #     "total_page": totalPage,
    #     "page_curren": int(pageCurren),
    #     "page_size": int(pageSize),
    #     "pagination_list": pagination_list
    # }

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
