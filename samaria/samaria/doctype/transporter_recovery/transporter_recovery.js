// Transporter Recovery — Client-side controller
// Frappe v15

frappe.ui.form.on("Transporter Recovery", {
	original_amount:  (frm) => frm.trigger("calc_pending"),
	recovered_amount: (frm) => frm.trigger("calc_pending"),

	calc_pending: function (frm) {
		const pending = Math.max(0, flt(frm.doc.original_amount) - flt(frm.doc.recovered_amount));
		frm.set_value("pending_amount", pending);
		const recovered = flt(frm.doc.recovered_amount);
		const original  = flt(frm.doc.original_amount);
		if (original > 0) {
			if (recovered >= original) {
				frm.set_value("status", "Recovered");
			} else if (recovered > 0) {
				frm.set_value("status", "Partial");
			}
		}
	}
});
