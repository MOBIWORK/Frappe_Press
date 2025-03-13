// Copyright (c) 2024, Mobiwork and contributors
// For license information, please see license.txt

frappe.ui.form.on('MBW Detail EInvoice', {
	cancel_and_redo: function (frm, cdt, cdn) {
		let item = locals[cdt][cdn];
		if (item.status == 'Pending processing') {
			frappe.call({
				method: 'press.api.einvoice.einvoice.retry_action_einvoice',
				type: 'POST',
				args: { data: item },
				callback: function (r) {
					if (!r.exc) {
						if (r.message?.code == 200) {
							frappe.msgprint(__(r.message?.msg));
						} else {
							frappe.throw(__(r.message?.msg));
						}
					} else {
						frappe.throw(__('An error occurred, please try again.'));
					}
				},
				async: true,
			});
		} else {
			frappe.throw(
				__(
					'Can only be performed when the record is in the `Pending processing` status.'
				)
			);
		}
	},
});
