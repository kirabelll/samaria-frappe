// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporter Recovery', {
	original_amount: function(frm) {
		calculate_pending(frm);
	},
	recovered_amount: function(frm) {
		calculate_pending(frm);
	}
});

function calculate_pending(frm) {
	let orig = flt(frm.doc.original_amount);
	let rec = flt(frm.doc.recovered_amount);
	frm.set_value('pending_amount', Math.max(0, orig - rec));
}
