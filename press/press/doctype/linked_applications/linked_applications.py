# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LinkedApplications(Document):
    pass


@frappe.whitelist()
def get_filter_group(cluster):
    servers = frappe.get_all("Server", filters={"cluster": cluster}, fields=["name"])
    servers = [server.name for server in servers]
    groups = frappe.get_all("Release Group Server", filters={"server": ('in', servers)}, fields=["parent"])
    groups = [group.parent for group in groups]
    return {'groups': groups}
