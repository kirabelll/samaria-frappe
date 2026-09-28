// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transport Association', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Transporters'), function() {
				frappe.set_route('List', 'Transporter', { association: frm.doc.name });
			}, __('Actions'));
		}
	}
});
