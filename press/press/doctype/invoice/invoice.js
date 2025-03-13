// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice', {
	refresh: function (frm) {
		let actions;
		if ([1, 2].includes(frm.doc.docstatus)) {
			actions = frm.events.get_action_ei(frm);
			// console.log(actions);
		}

		if (frm.doc.stripe_invoice_id) {
			frm.add_web_link(
				`https://dashboard.stripe.com/invoices/${frm.doc.stripe_invoice_id}`,
				'View Stripe Invoice'
			);
		}
		if (frm.doc.frappe_invoice) {
			frm.add_web_link(
				`https://frappe.io/app/sales-invoice/${frm.doc.frappe_invoice}`,
				'View Frappe Invoice'
			);
		}
		if (frm.doc.frappe_partner_order) {
			frm.add_web_link(
				`https://frappe.io/app/partner-order/${frm.doc.frappe_partner_order}`,
				'View Frappe Partner Order'
			);
		}

		if (frm.doc.docstatus == 1 && frm.doc.status == 'Paid') {
			// hidden button cancel
			if (actions?.cancel) {
				frm.page.btn_secondary.show();
			} else {
				frm.page.btn_secondary.hide();
			}

			if (actions?.create_ei) {
				frm.add_custom_button(
					'Create invoice',
					() => frm.events.create_einvoice(frm),
					__('EInvoice')
				);
			}

			if (actions?.sign_ei) {
				frm.add_custom_button(
					__('Sign invoice'),
					() => frm.events.sign_einvoice(frm),
					__('EInvoice')
				);
			}

			// add btn get status einvoice
			if (actions?.update_status_ei) {
				frm.add_custom_button(
					__('Update status'),
					() => frm.events.update_status_einvoice(frm),
					__('EInvoice')
				);
			}

			// add btn cancel einvoice
			if (actions?.cancel_ei) {
				frm.add_custom_button(
					__('Revoke invoice'),
					() => {
						frappe.prompt(
							[
								{
									label: __('Reason'),
									fieldname: 'reason',
									fieldtype: 'Small Text',
									reqd: 1,
									description: __(
										'The reason must be at least 30 characters long.'
									),
								},
							],
							(values) => {
								if (!values.reason || values.reason.trim().length < 30) {
									let lenReason = values.reason
										? values.reason.trim().length
										: 0;
									let msg = __(
										'The reason must be at least 30 characters long. Currently, it has {lenReason} characters.'
									).replaceAll('{lenReason}', lenReason);
									frappe.msgprint({
										title: __('Please fill in all required data'),
										message: msg,
										indicator: 'orange',
									});
									return false;
								}
								frm.events.cancel_einvoice(frm, values.reason);
							},
							__('Revoke EInvoice'),
							__('Confirm')
						);
					},
					__('EInvoice')
				);
			}

			// add btn einvoice replacement
			if (actions?.replace_ei) {
				let invoice_id = frm.events.get_original_invoice(frm, 0);
				frm.add_custom_button(
					__('Create a replacement invoice'),
					() => {
						frappe.prompt(
							[
								{
									label: __('Invoice to be replaced'),
									fieldname: 'invoice_id',
									fieldtype: 'Link',
									options: 'Sales Invoice',
									default: invoice_id,
									reqd: 1,
									read_only: 1,
								},
								{
									label: __('Reason'),
									fieldname: 'reason',
									fieldtype: 'Small Text',
									reqd: 1,
									description: __(
										'The reason must be at least 30 characters long.'
									),
								},
							],
							(values) => {
								if (!values.reason || values.reason.length < 30) {
									let lenReason = values.reason
										? values.reason.trim().length
										: 0;
									let msg = __(
										'The reason must be at least 30 characters long. Currently, it has {lenReason} characters.'
									).replaceAll('{lenReason}', lenReason);
									frappe.msgprint({
										title: __('Please fill in all required data'),
										message: msg,
										indicator: 'orange',
									});
									return false;
								}
								frm.events.einvoice_replacement(frm, values);
							},
							__('Create a replacement EInvoice'),
							__('Confirm')
						);
					},
					__('EInvoice')
				);
			}
		}

		if (frm.doc.docstatus == 2) {
			if (actions?.amend) {
				frm.page.btn_primary.show();
			} else {
				frm.page.btn_primary.hide();
			}
		} else {
			frm.page.btn_primary.show();
		}

		// if (frm.doc.status == 'Paid' && !frm.doc.frappe_invoice) {
		// 	let btn = frm.add_custom_button('Create Invoice on frappe.io', () => {
		// 		frm
		// 			.call({
		// 				doc: frm.doc,
		// 				method: 'create_invoice_on_frappeio',
		// 				btn,
		// 			})
		// 			.then((r) => {
		// 				if (r.message) {
		// 					frappe.msgprint(
		// 						`Sales Invoice ${r.message} created successfully.`
		// 					);
		// 				}
		// 				frm.refresh();
		// 			});
		// 	});
		// }

		if (frm.doc.status == 'Paid' && frm.doc.stripe_invoice_id) {
			let btn = frm.add_custom_button('Refund Invoice', () =>
				frappe.confirm(
					'This will refund the total amount paid on this invoice from Stripe. Continue?',
					() =>
						frm
							.call({
								doc: frm.doc,
								method: 'refund',
								btn,
							})
							.then((r) => {
								if (r.message) {
									frappe.msgprint(`Refunded successfully.`);
								}
								frm.refresh();
							})
				)
			);
		}

		if (frm.doc.status == 'Invoice Created') {
			let btn = frm.add_custom_button(
				'Finalize Invoice',
				() => {
					frappe.confirm(
						"This action will finalize the Stripe Invoice and charge the customer's card. Continue?",
						() => {
							frm
								.call({
									doc: frm.doc,
									method: 'finalize_stripe_invoice',
									btn,
								})
								.then((r) => frm.refresh());
						}
					);
				},
				'Stripe Invoice'
			);
		}

		if (frm.doc.stripe_invoice_url) {
			let btn = frm.add_custom_button(
				'Refresh Payment Link',
				() => {
					frm
						.call({
							doc: frm.doc,
							method: 'refresh_stripe_payment_link',
							btn,
						})
						.then((r) => {
							frm.refresh();
							frappe.utils.copy_to_clipboard(r.message);
							frappe.msgprint({
								title: 'Stripe Payment Link Updated',
								indicator: 'green',
								message: 'The Link has been copied to the clipboard.',
							});
						});
				},
				'Stripe Invoice'
			);
		}

		if (frm.doc.docstatus == 1 && frm.doc.stripe_invoice_id) {
			let btn = frm.add_custom_button(
				'Change Status',
				() => {
					let d = new frappe.ui.Dialog({
						title: 'Change Stripe Invoice Status',
						fields: [
							{
								label: 'Status',
								fieldname: 'status',
								fieldtype: 'Select',
								options: ['Paid', 'Uncollectible', 'Void'],
							},
						],
						primary_action({ status }) {
							frm
								.call({
									doc: frm.doc,
									method: 'change_stripe_invoice_status',
									args: {
										status,
									},
									btn,
								})
								.then((r) => frm.refresh());
						},
					});
					d.show();
				},
				'Stripe Invoice'
			);
		}

		if (frm.doc.docstatus === 0) {
			let btn = frm.add_custom_button('Finalize Invoice', () =>
				frappe.confirm(
					'This action will apply credits (if applicable) and generate a Stripe invoice if the amount due is greater than 0. ' +
						'If a Stripe invoice was generated already, it will be voided and a new one will be generated. Continue?',
					() =>
						frm
							.call({
								doc: frm.doc,
								method: 'finalize_invoice',
								btn,
							})
							.then(() => {
								frm.refresh();
							})
				)
			);
		}
	},

	get_original_invoice: function (frm, type_invoice) {
		let rs = '';
		frappe.call({
			method: 'press.api.einvoice.einvoice.get_original_invoice',
			type: 'POST',
			args: { name: frm.doc.name, type_invoice: type_invoice },
			callback: function (r) {
				if (!r.exc) {
					rs = r.message ? r.message : '';
				}
			},
			async: false,
		});

		return rs;
	},

	get_action_ei: function (frm) {
		let rs = {};
		frappe.call({
			method: 'press.api.einvoice.einvoice.get_action_einvoice',
			type: 'POST',
			args: { name: frm.doc.name },
			callback: function (r) {
				if (!r.exc) {
					rs = r.message;
				}
			},
			async: false,
		});

		return rs;
	},

	custom_get_pdf_invoice_link(frm) {
		let d = frappe.msgprint(
			__('Retrieving the invoice PDF file link, please wait a moment...')
		);

		frappe.call({
			method: 'press.api.einvoice.einvoice.get_link_pdf_file',
			type: 'POST',
			args: { name: frm.doc.name, type_pdf: 'invoice' },
			callback: function (r) {
				if (!r.exc) {
					if (r.message?.code == 200) {
						setTimeout(() => {
							d.hide();
							window.open(r.message?.data?.link_pdf, '_blank');
						}, 300);
					} else {
						d.clear();
						frappe.throw(__(r.message?.msg));
					}
				} else {
					d.clear();
					frappe.throw(__('An error occurred, please try again.'));
				}
			},
			async: true,
		});
	},
	custom_get_pdf_cancellation_report_link(frm) {
		let d = frappe.msgprint(
			__(
				'Retrieving the cancellation report PDF file link, please wait a moment...'
			)
		);

		frappe.call({
			method: 'press.api.einvoice.einvoice.get_link_pdf_file',
			type: 'POST',
			args: { name: frm.doc.name, type_pdf: 'cancellation_report' },
			callback: function (r) {
				if (!r.exc) {
					if (r.message?.code == 200) {
						setTimeout(() => {
							d.hide();
							window.open(r.message?.data?.link_pdf, '_blank');
						}, 300);
					} else {
						d.clear();
						frappe.throw(__(r.message?.msg));
					}
				} else {
					d.clear();
					frappe.throw(__('An error occurred, please try again.'));
				}
			},
			async: true,
		});
	},

	// handle create einvoice
	create_einvoice: function (frm) {
		// frappe.msgprint('Đang cập nhật...');
		// return;
		frappe.call({
			method: 'press.api.einvoice.einvoice.create_einvoice',
			type: 'POST',
			args: { name: frm.doc.name },
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
	},

	// handle sign einvoice
	sign_einvoice: function (frm) {
		// frappe.msgprint('Đang cập nhật...');
		// return;
		frappe.call({
			method: 'press.api.einvoice.einvoice.sign_einvoice',
			type: 'POST',
			args: { name: frm.doc.name },
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
	},

	// update status invoice
	update_status_einvoice: function (frm) {
		// frappe.msgprint('Đang cập nhật...');
		// return;
		frappe.call({
			method: 'press.api.einvoice.einvoice.update_status_einvoice',
			type: 'POST',
			args: { name: frm.doc.name },
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
	},

	// handle cancel einvoice
	cancel_einvoice: function (frm, reason) {
		// frappe.msgprint('Đang cập nhật...');
		// return;
		frappe.call({
			method: 'press.api.einvoice.einvoice.cancel_einvoice',
			type: 'POST',
			args: { name: frm.doc.name, reason: reason },
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
	},

	// handle replace electronic invoices
	einvoice_replacement: function (frm, data) {
		// frappe.msgprint('Đang cập nhật...');
		// return;
		frappe.call({
			method: 'press.api.einvoice.einvoice.einvoice_replacement',
			type: 'POST',
			args: { name: frm.doc.name, reason: data?.reason },
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
	},
});


{% include 'press/press/doctype/mbw_detail_einvoice/mbw_detail_einvoice.js' %}