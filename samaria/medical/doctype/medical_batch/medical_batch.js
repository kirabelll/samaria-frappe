// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Batch', {
	refresh: function(frm) {
		if (frm.doc.expiry_date) {
			let diff = frappe.datetime.get_diff(frm.doc.expiry_date, frappe.datetime.get_today());
			if (diff < 0) {
				frm.dashboard.set_headline_alert(__('This batch has expired!'), 'red');
			} else if (diff < 90) {
				frm.dashboard.set_headline_alert(__('Batch expires in less than 90 days (' + diff + ' days remaining)'), 'orange');
			}
		}
	}
});
