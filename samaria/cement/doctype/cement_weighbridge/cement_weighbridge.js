// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cement Weighbridge', {
	gross_weight: function(frm) {
		calculate_net_weight(frm);
	},
	tare_weight: function(frm) {
		calculate_net_weight(frm);
	}
});

function calculate_net_weight(frm) {
	let gross = flt(frm.doc.gross_weight);
	let tare = flt(frm.doc.tare_weight);
	frm.set_value('net_weight', Math.max(0, gross - tare));
}
