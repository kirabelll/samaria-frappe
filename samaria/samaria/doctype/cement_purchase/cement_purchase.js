// Cement Purchase — Client-side controller
// Frappe v15

frappe.ui.form.on("Cement Purchase", {
	quantity_tons: (frm) => frm.trigger("recalculate"),
	unit_price:    (frm) => frm.trigger("recalculate"),
	vat_rate:      (frm) => frm.trigger("recalculate"),
	paid_amount:   (frm) => frm.trigger("recalculate"),

	recalculate: function (frm) {
		const base = flt(frm.doc.quantity_tons) * flt(frm.doc.unit_price);
		const vat  = base * (flt(frm.doc.vat_rate) / 100.0);
		frm.set_value("vat_amount",   vat);
		frm.set_value("total_amount", base + vat);

		const paid  = flt(frm.doc.paid_amount);
		const total = base + vat;

		if (paid >= total && total > 0) {
			frm.set_value("payment_status", "Paid");
		} else if (paid > 0) {
			frm.set_value("payment_status", "Partial");
		} else {
			frm.set_value("payment_status", "Unpaid");
		}
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Liftings"), function () {
				frappe.set_route("List", "Cement Lifting", { purchase: frm.doc.name });
			}, __("Links"));
		}
	}
});
