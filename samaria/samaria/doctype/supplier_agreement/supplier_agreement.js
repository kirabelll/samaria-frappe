// Supplier Agreement — Client-side controller (mirrors Sales Agreement)
// Frappe v15

frappe.ui.form.on("Supplier Agreement", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Deliveries"), function () {
				frappe.set_route("List", "Aggregate Delivery", { supplier: frm.doc.supplier });
			}, __("Links"));
		}
	}
});

frappe.ui.form.on("Supplier Agreement Item", {
	qty:        (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	unit_price: (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	price_type: (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	items_remove: (frm) => update_total(frm)
});

function calc_item(frm, cdt, cdn) {
	const row  = locals[cdt][cdn];
	const base = flt(row.qty) * flt(row.unit_price);
	frappe.model.set_value(cdt, cdn, "amount", row.price_type === "incl" ? base * 1.15 : base);
	update_total(frm);
}

function update_total(frm) {
	frm.set_value("total_amount",
		(frm.doc.items || []).reduce((s, r) => s + flt(r.amount), 0)
	);
}
