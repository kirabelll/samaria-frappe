// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Store Issue', {
	setup: function(frm) {
		frm.set_query('batch', 'items', function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let filters = {
				status: 'Available',
				quantity: ['>', 0]
			};
			if (row.item_code) {
				filters['item_code'] = row.item_code;
			}
			return { filters: filters };
		});
	}
});

frappe.ui.form.on('Medical Store Issue Item', {
	batch: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.batch) {
			frappe.db.get_doc('Medical Batch', row.batch).then(batch => {
				frappe.model.set_value(cdt, cdn, 'batch_no', batch.batch_no);
				frappe.model.set_value(cdt, cdn, 'expiry_date', batch.expiry_date);
				frappe.model.set_value(cdt, cdn, 'item_name', batch.item_name);
				if (!row.item_code) {
					frappe.model.set_value(cdt, cdn, 'item_code', batch.item_code);
				}
			});
		}
	},
	quantity: function(frm, cdt, cdn) {
		calculate_issue_item(frm, cdt, cdn);
	},
	unit_price: function(frm, cdt, cdn) {
		calculate_issue_item(frm, cdt, cdn);
	}
});

function calculate_issue_item(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.quantity);
	let price = flt(row.unit_price);
	frappe.model.set_value(cdt, cdn, 'total_amount', qty * price);

	let total = 0;
	(frm.doc.items || []).forEach(item => {
		total += flt(item.total_amount);
	});
	frm.set_value('total_amount', total);
}
