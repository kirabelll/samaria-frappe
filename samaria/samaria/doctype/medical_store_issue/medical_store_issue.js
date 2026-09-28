frappe.ui.form.on('MedicalStoreIssue', {
	// Parent triggers
});

frappe.ui.form.on('MedicalStoreIssueItem', {
	qty: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.total_amount = flt(row.qty) * flt(row.unit_price);
		frm.refresh_field('items');
		recalc_issue_totals(frm);
	},
	unit_price: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.total_amount = flt(row.qty) * flt(row.unit_price);
		frm.refresh_field('items');
		recalc_issue_totals(frm);
	},
	batch: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.batch) {
			frappe.db.get_value('Medical Batch', row.batch, ['batch_no', 'expiry_date', 'cost_price'], function(val) {
				if (val) {
					row.batch_no = val.batch_no;
					row.expiry_date = val.expiry_date;
					if (!row.unit_price && val.cost_price) {
						row.unit_price = val.cost_price;
						row.total_amount = flt(row.qty) * flt(row.unit_price);
					}
					frm.refresh_field('items');
					recalc_issue_totals(frm);
				}
			});
		}
	},
	items_remove: function(frm) {
		recalc_issue_totals(frm);
	}
});

function recalc_issue_totals(frm) {
	var total = 0;
	(frm.doc.items || []).forEach(function(row) {
		total += flt(row.total_amount);
	});
	frm.set_value('total_amount', total);
}
