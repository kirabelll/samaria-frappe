// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cement Coupon', {
	refresh: function(frm) {
		if (frm.doc.status === 'Collected' || frm.doc.status === 'In Custody') {
			frm.add_custom_button(__('Hand Over to Driver'), function() {
				frappe.prompt([
					{ fieldname: 'handed_over_to', fieldtype: 'Data', label: 'Handed Over To', reqd: 1 },
					{ fieldname: 'handover_date', fieldtype: 'Date', label: 'Handover Date', default: frappe.datetime.get_today() }
				], values => {
					frm.set_value('handed_over_to', values.handed_over_to);
					frm.set_value('handover_date', values.handover_date);
					frm.set_value('status', 'Handed Over');
					frm.save();
				}, __('Handover Details'));
			}, __('Actions'));
		}
	}
});
