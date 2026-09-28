// Copyright (c) 2026, Samaria and contributors
// For license information, please see license.txt

frappe.ui.form.on('Samaria Setting', {
	refresh: function(frm) {
		frm.add_custom_button(__('Ping API'), function() {
			frappe.call({
				method: 'samaria.api.v1.ping',
				callback: function(r) {
					if (r.message && r.message.status === 'success') {
						frappe.show_alert({
							message: __('Connected: ') + r.message.message,
							indicator: 'green'
						});
					}
				}
			});
		}, __('Actions'));
	}
});
