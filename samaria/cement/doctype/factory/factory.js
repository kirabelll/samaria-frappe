// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Factory', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Purchases'), function() {
				frappe.set_route('List', 'Cement Purchase', { factory: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Coupons'), function() {
				frappe.set_route('List', 'Cement Coupon', { factory: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Liftings'), function() {
				frappe.set_route('List', 'Cement Lifting', { factory: frm.doc.name });
			}, __('Views'));
		}
	}
});
