// Medical Store Issue — Client-side controller
// Frappe v15

frappe.ui.form.on("Medical Store Issue", {
	refresh: function (frm) {
		if (frm.doc.request && !frm.is_new()) {
			frm.add_custom_button(__("View Request"), function () {
				frappe.set_route("Form", "Medical Request", frm.doc.request);
			}, __("Links"));
		}
	}
});

frappe.ui.form.on("Medical Store Issue Item", {
	batch: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.batch) {
			frappe.db.get_value("Medical Batch", row.batch,
				["batch_no", "expiry_date", "cost_price"],
				(r) => {
					if (r) {
						frappe.model.set_value(cdt, cdn, "batch_no",     r.batch_no);
						frappe.model.set_value(cdt, cdn, "expiry_date",  r.expiry_date);
						if (!flt(row.unit_price)) {
							frappe.model.set_value(cdt, cdn, "unit_price", r.cost_price);
						}
						calc_row(frm, cdt, cdn);
					}
				}
			);
		}
	},
	qty:        (frm, cdt, cdn) => calc_row(frm, cdt, cdn),
	unit_price: (frm, cdt, cdn) => calc_row(frm, cdt, cdn),
	items_remove: (frm) => update_total(frm)
});

function calc_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "total_amount", flt(row.qty) * flt(row.unit_price));
	update_total(frm);
}

function update_total(frm) {
	const total = (frm.doc.items || []).reduce((s, r) => s + flt(r.total_amount), 0);
	frm.set_value("total_amount", total);
}
