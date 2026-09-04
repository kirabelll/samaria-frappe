frappe.ui.form.on('Supplier Agreement', {
	refresh: function(frm) {
		if (frm.doc.status === 'Deactivated') {
			frm.add_custom_button(__('Reactivate Agreement'), function() {
				frm.set_value('status', 'Active');
				frm.save();
			}, __('Actions'));
		} else if (frm.doc.status === 'Active') {
			frm.add_custom_button(__('Deactivate Agreement'), function() {
				frm.set_value('status', 'Deactivated');
				frm.save();
			}, __('Actions'));
		}
	}
});

frappe.ui.form.on('Supplier Agreement Item', {
	qty: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	unit_price: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	price_type: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	}
});

function calculate_item_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.qty);
	let price = flt(row.unit_price);
	let amount = (row.price_type === 'incl') ? (qty * price * 1.15) : (qty * price);
	frappe.model.set_value(cdt, cdn, 'amount', amount);

	let total = 0;
	(frm.doc.items || []).forEach(d => {
		total += flt(d.amount);
	});
	frm.set_value('total_amount', total);
}
