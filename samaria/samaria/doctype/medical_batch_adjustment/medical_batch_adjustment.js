// Medical Batch Adjustment — Client-side controller
// Frappe v15

frappe.ui.form.on("Medical Batch Adjustment Item", {
	batch: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.batch) {
			frappe.db.get_value("Medical Batch", row.batch, "quantity", (r) => {
				if (r) {
					frappe.model.set_value(cdt, cdn, "current_qty",  r.quantity);
					frappe.model.set_value(cdt, cdn, "adjusted_qty", r.quantity);
					frappe.model.set_value(cdt, cdn, "variance",     0);
				}
			});
		}
	},

	adjusted_qty: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const variance = flt(row.adjusted_qty) - flt(row.current_qty);
		frappe.model.set_value(cdt, cdn, "variance", variance);
	}
});
