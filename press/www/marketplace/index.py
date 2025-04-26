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
    category = args.get('category', '')
    type_overview = args.get('type_overview', '')
    context.category = category
    context.type_overview = type_overview
    context.no_cache = 1

    if not type_overview:
        slides = frappe.db.get_all(
            'Marketplace Slide',
            filters={
                'enabled': 1
            },
            fields=['name', 'content', 'style'],
            order_by='level asc'
        )
        context.slides = slides

    if category:
        pageCurren = args.get('page') if args.get(
            'page') and int(args.get('page')) > 1 else '1'
        pageSize = args.get('page_size') if args.get(
            'page_size') and int(args.get('page_size')) > 1 else '20'
        skipRow = str(int(pageSize) * (int(pageCurren)-1))
        text_search = args.get('text_search', '')
        context.text_search = text_search
        context.category = category

        str_query = """
            SELECT
                COUNT(*) AS total_apps
            FROM
                `tabMarketplace App` marketplace
        """

        if category != "all_category":
            str_query += f"""
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

        if category != "all_category":
            str_query += f"""
            AND
                categories.category = '{category}'
            """
        str_query += """
            GROUP BY
                marketplace.name;
        """

        rs_query = frappe.db.sql(
            str_query,
            as_dict=True,
        )
        if rs_query:
            total_all_published_apps = rs_query[0].get('total_apps')
        else:
            total_all_published_apps = 0

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

        str_query = """
        SELECT
                marketplace.name,
                marketplace.title,
                marketplace.image,
                marketplace.route,
                marketplace.description,
                marketplace.subscription_type,
                COUNT(*) AS total_installs
            FROM
                `tabMarketplace App` marketplace
            LEFT JOIN
                `tabSite App` site
            ON
                site.app = marketplace.app
        """

        if category != "all_category":
            str_query += f"""
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

        if category != "all_category":
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
        for app in all_published_apps:
            info_app = frappe.get_doc(
                "Marketplace App",
                {"name": app.get('name')}
            )
            user_reviews = info_app.get_user_reviews()
            ratings_summary = info_app.get_user_ratings_summary(user_reviews)
            app['ratings_summary'] = ratings_summary

        context.apps = all_published_apps

        str_query = f"""
            SELECT
                category.name,
                category.content
            FROM
                `tabMarketplace App Category` category
            WHERE
                category.name = '{category}';
        """

        detail_category = {}
        list_category = frappe.db.sql(
            str_query,
            as_dict=True,
        )
        if len(list_category):
            info_category = list_category[0]
        else:
            info_category = None
        context.info_category = info_category
    else:
        # lay category hien thi
        str_query = """
            SELECT
                category.name,
                category.content,
                category.level
            FROM
                `tabMarketplace App Category` category
            WHERE
                category.show_in_dashboard = 1
            ORDER BY
                level ASC;
        """
        categories_show = frappe.db.sql(
            str_query,
            as_dict=True,
        )

        apps_show = []
        for cate in categories_show:
            name_cate = cate.get('name')

            str_query = f"""
                SELECT
                    marketplace.name,
                    marketplace.title,
                    marketplace.image,
                    marketplace.route,
                    marketplace.description,
                    marketplace.subscription_type,
                    marketplace.level
                FROM
                    `tabMarketplace App` marketplace
                INNER JOIN
                `tabMarketplace App Categories` categories
                ON
                    categories.parent = marketplace.name
                WHERE
                    marketplace.status = "Published"
                AND
                    categories.category = '{name_cate}'
                GROUP BY
                    marketplace.name
                ORDER BY
                    level ASC
                OFFSET 0 ROWS
                FETCH NEXT 4 ROWS ONLY;
            """

            most_used_apps = frappe.db.sql(
                str_query,
                as_dict=True,
            )
            for app in most_used_apps:
                info_app = frappe.get_doc(
                    "Marketplace App",
                    {"name": app.get('name')}
                )
                user_reviews = info_app.get_user_reviews()
                ratings_summary = info_app.get_user_ratings_summary(
                    user_reviews)
                app['ratings_summary'] = ratings_summary

            info_item = {
                'content': cate.get('content'),
                'name_category': cate.get('name'),
                'data': most_used_apps
            }
            apps_show.append(info_item)

        context.apps_show = apps_show

    ###
    # for app in all_published_apps:
    #     app["categories"] = frappe.db.get_all(
    #         "Marketplace App Categories", {"parent": app["name"]}, pluck="category"
    #     )

    context.categories = sorted(
        frappe.db.get_all("Marketplace App Categories",
                          pluck="category", distinct=True)
    )
    # if "Featured" in context.categories:
    #     context.categories.remove("Featured")
    #     context.categories.insert(0, "Featured")

    # featured_apps = frappe.get_all(
    #     "Featured App",
    #     filters={"parent": "Marketplace Settings"},
    #     pluck="app",
    #     order_by="idx",
    # )

    # context.featured_apps = sorted(
    #     filter(lambda x: x.name in featured_apps, all_published_apps),
    #     key=lambda y: featured_apps.index(y.name),
    # )

    context.metatags = {
        "title": "MBWCloud Marketplace",
        "description": "One Click Apps for your MBW Sites",
        "og:type": "website",
    }
