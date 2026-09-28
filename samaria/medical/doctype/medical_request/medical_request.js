// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Request', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.status !== 'Dispatched' && frm.doc.status !== 'Delivered') {
			frm.add_custom_button(__('Create Store Issue'), function() {
				frappe.call({
					method: 'samaria.api.medical.create_store_issue_from_request',
					args: {
						request_id: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frappe.set_route('Form', 'Medical Store Issue', r.message);
						}
					}
				});
			}, __('Actions'));
		}
	}
});
