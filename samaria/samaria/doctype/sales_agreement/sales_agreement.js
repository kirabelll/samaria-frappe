// Sales Agreement — Client-side controller
// Frappe v15

frappe.ui.form.on("Sales Agreement", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			if (frm.doc.status === "Active") {
				frm.add_custom_button(__("Deactivate"), function () {
					frm.call("deactivate").then(() => frm.reload_doc());
				}, __("Actions"));
			} else if (frm.doc.status === "Deactivated") {
				frm.add_custom_button(__("Reactivate"), function () {
					frm.call("reactivate").then(() => frm.reload_doc());
				}, __("Actions"));
			}
			frm.add_custom_button(__("View Deliveries"), function () {
				frappe.set_route("List", "Aggregate Delivery", { customer: frm.doc.customer });
			}, __("Links"));
		}
	}
});

frappe.ui.form.on("Sales Agreement Item", {
	qty:        (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	unit_price: (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	price_type: (frm, cdt, cdn) => calc_item(frm, cdt, cdn),
	items_remove: (frm) => update_total(frm)
});

function calc_item(frm, cdt, cdn) {
	const row  = locals[cdt][cdn];
	const base = flt(row.qty) * flt(row.unit_price);
	const amt  = row.price_type === "incl" ? base * 1.15 : base;
	frappe.model.set_value(cdt, cdn, "amount", amt);
	update_total(frm);
}

function update_total(frm) {
	const total = (frm.doc.items || []).reduce((s, r) => s + flt(r.amount), 0);
	frm.set_value("total_amount", total);
}
