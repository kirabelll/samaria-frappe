// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Truck', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Delivery History'), function() {
				frappe.set_route('List', 'Aggregate Delivery', { truck: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Cement Liftings'), function() {
				frappe.set_route('List', 'Cement Lifting', { truck: frm.doc.name });
			}, __('Views'));
		}
	}
});
