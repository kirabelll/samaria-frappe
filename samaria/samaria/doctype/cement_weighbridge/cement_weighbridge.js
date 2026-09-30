// Cement Weighbridge — Client-side controller
// Frappe v15

frappe.ui.form.on("Cement Weighbridge", {
	gross_weight: (frm) => frm.trigger("calc_net"),
	tare_weight:  (frm) => frm.trigger("calc_net"),

	calc_net: function (frm) {
		const net = Math.max(0, flt(frm.doc.gross_weight) - flt(frm.doc.tare_weight));
		frm.set_value("net_weight", net);
	}
});
