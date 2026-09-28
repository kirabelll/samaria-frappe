// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporter', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Assigned Trucks'), function() {
				frappe.set_route('List', 'Truck', { transporter: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Agreements'), function() {
				frappe.set_route('List', 'Transporter Agreement', { transporter: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Deliveries'), function() {
				frappe.set_route('List', 'Aggregate Delivery', { transporter: frm.doc.name });
			}, __('Views'));

			frm.add_custom_button(__('Recoveries / Claims'), function() {
				frappe.set_route('List', 'Transporter Recovery', { transporter: frm.doc.name });
			}, __('Views'));
		}
	}
});
