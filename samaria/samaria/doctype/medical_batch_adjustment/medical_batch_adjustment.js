frappe.ui.form.on('Medical Batch Adjustment Item', {
	batch: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.batch) {
			frappe.db.get_value('Medical Batch', row.batch, 'quantity', function(val) {
				if (val && val.quantity !== undefined) {
					frappe.model.set_value(cdt, cdn, 'current_qty', val.quantity);
					frappe.model.set_value(cdt, cdn, 'adjusted_qty', val.quantity);
					frappe.model.set_value(cdt, cdn, 'variance', 0);
				}
			});
		}
	},
	adjusted_qty: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let curr = flt(row.current_qty);
		let adj = flt(row.adjusted_qty);
		frappe.model.set_value(cdt, cdn, 'variance', adj - curr);
	}
});
