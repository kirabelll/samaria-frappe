// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cement Purchase', {
	quantity_tons: function(frm) {
		calculate_purchase_total(frm);
	},
	unit_price: function(frm) {
		calculate_purchase_total(frm);
	},
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Issue Coupon'), function() {
				frappe.new_doc('Cement Coupon', {
					factory: frm.doc.factory,
					cement_purchase: frm.doc.name
				});
			}, __('Actions'));

			frm.add_custom_button(__('Record Lifting'), function() {
				frappe.new_doc('Cement Lifting', {
					factory: frm.doc.factory,
					cement_purchase: frm.doc.name
				});
			}, __('Actions'));
		}
	}
});

function calculate_purchase_total(frm) {
	let qty = flt(frm.doc.quantity_tons);
	let price = flt(frm.doc.unit_price);
	frm.set_value('total_amount', qty * price);
}
