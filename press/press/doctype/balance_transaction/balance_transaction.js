// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Balance Transaction', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button('Finalize unpaid invoices', () => {
				let d = frappe.msgprint('Đang xử lý dưới nền...');
				frappe
					.call({
						method:
							'press.press.doctype.balance_transaction.balance_transaction.handle_finalize_unpaid_invoices',
						args: {
							team: frm.doc.team,
						},
					})
					.then((r) => {
						if (r.exc) {
							d.clear();
							frappe.throw(r.exc);
						}
					});
			});
		}
	},
});
