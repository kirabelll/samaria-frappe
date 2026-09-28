frappe.ui.form.on('CementPurchase', {
	quantity_tons: function(frm) {
		frm.trigger('calculate_totals');
	},
	unit_price: function(frm) {
		frm.trigger('calculate_totals');
	},
	vat_rate: function(frm) {
		frm.trigger('calculate_totals');
	},
	paid_amount: function(frm) {
		frm.trigger('calculate_totals');
	},
	calculate_totals: function(frm) {
		var qty = flt(frm.doc.quantity_tons);
		var price = flt(frm.doc.unit_price);
		var base = qty * price;
		var vat_r = flt(frm.doc.vat_rate);
		var vat_amt = (vat_r / 100.0) * base;
		var total = base + vat_amt;
		var paid = flt(frm.doc.paid_amount);

		frm.set_value('vat_amount', vat_amt);
		frm.set_value('total_amount', total);

		if (frm.is_new() || frm.doc.balance_remaining === undefined || frm.doc.balance_remaining === null) {
			frm.set_value('balance_remaining', qty);
		}

		if (paid >= total && total > 0) {
			frm.set_value('payment_status', 'Paid');
		} else if (paid > 0) {
			frm.set_value('payment_status', 'Partial');
		} else {
			frm.set_value('payment_status', 'Unpaid');
		}
	}
});
