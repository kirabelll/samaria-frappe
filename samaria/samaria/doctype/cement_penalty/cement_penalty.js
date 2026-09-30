// Cement Penalty — Client-side controller
// Frappe v15

frappe.ui.form.on("Cement Penalty", {
	shortage_qty:     (frm) => frm.trigger("calc_penalty"),
	penalty_rate:     (frm) => frm.trigger("calc_penalty"),
	recovered_amount: (frm) => frm.trigger("update_status"),

	calc_penalty: function (frm) {
		if (flt(frm.doc.shortage_qty) > 0 && flt(frm.doc.penalty_rate) > 0) {
			frm.set_value("penalty_amount", flt(frm.doc.shortage_qty) * flt(frm.doc.penalty_rate));
		}
		frm.trigger("update_status");
	},

	update_status: function (frm) {
		const recovered = flt(frm.doc.recovered_amount);
		const penalty   = flt(frm.doc.penalty_amount);
		if (penalty > 0) {
			if (recovered >= penalty) {
				frm.set_value("recovery_status", "Recovered");
			} else if (recovered > 0) {
				frm.set_value("recovery_status", "Deducted");
			}
		}
	}
});
