// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cement Penalty', {
	shortage_qty: function(frm) {
		calculate_penalty_amount(frm);
	},
	penalty_rate: function(frm) {
		calculate_penalty_amount(frm);
	}
});

function calculate_penalty_amount(frm) {
	let qty = flt(frm.doc.shortage_qty);
	let rate = flt(frm.doc.penalty_rate);
	frm.set_value('penalty_amount', qty * rate);
}
