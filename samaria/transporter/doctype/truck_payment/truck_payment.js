// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Truck Payment', {
	total_gross_fee: function(frm) {
		calculate_payable(frm);
	},
	total_shortage_deduction: function(frm) {
		calculate_payable(frm);
	},
	association_deduction: function(frm) {
		calculate_payable(frm);
	},
	recovery_deduction: function(frm) {
		calculate_payable(frm);
	}
});

function calculate_payable(frm) {
	let gross = flt(frm.doc.total_gross_fee);
	let shortage = flt(frm.doc.total_shortage_deduction);
	let net = Math.max(0, gross - shortage);
	frm.set_value('total_net_payment', net);

	let assoc = flt(frm.doc.association_deduction);
	let rec = flt(frm.doc.recovery_deduction);
	frm.set_value('final_payable', Math.max(0, net - assoc - rec));
}
