// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporter Agreement', {
	refresh: function(frm) {
		// Custom actions
	}
});

frappe.ui.form.on('Transporter Pricing', {
	holding_capacity: function(frm, cdt, cdn) {
		calculate_category_row(frm, cdt, cdn);
	},
	unit_price: function(frm, cdt, cdn) {
		calculate_category_row(frm, cdt, cdn);
	}
});

function calculate_category_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.holding_capacity && row.unit_price) {
		frappe.model.set_value(cdt, cdn, 'total_price', flt(row.holding_capacity) * flt(row.unit_price));
	}
}
