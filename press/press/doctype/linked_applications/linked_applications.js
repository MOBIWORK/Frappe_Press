// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Linked Applications', {
	refresh: function (frm) {

	},
	cluster: function (frm) {
		frappe.call({
			method: "press.press.doctype.linked_applications.linked_applications.get_filter_group",
			args: {
				cluster: frm.doc.cluster,
			},
			callback: function (r) {
				frm.set_query("group", () => {
					return {
						filters: {
							name: ["in", r.message?.groups || []],
						},
					};
				});
			},
		});
	}
});
