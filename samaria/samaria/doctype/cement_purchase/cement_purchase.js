frappe.ui.form.on('Cement Purchase', {
	quantity_tons: function(frm) {
		calculate_purchase_totals(frm);
	},
	unit_price: function(frm) {
		calculate_purchase_totals(frm);
	},
	vat_rate: function(frm) {
		calculate_purchase_totals(frm);
	},
	paid_amount: function(frm) {
		calculate_purchase_totals(frm);
	}
});

function calculate_purchase_totals(frm) {
	let qty = flt(frm.doc.quantity_tons);
	let price = flt(frm.doc.unit_price);
	let baseTotal = qty * price;
	let vatRate = flt(frm.doc.vat_rate);
	let vatAmt = (vatRate / 100.0) * baseTotal;
	let total = baseTotal + vatAmt;

	frm.set_value('vat_amount', vatAmt);
	frm.set_value('total_amount', total);

	let paid = flt(frm.doc.paid_amount);
	if (paid >= total && total > 0) {
		frm.set_value('payment_status', 'Paid');
	} else if (paid > 0) {
		frm.set_value('payment_status', 'Partial');
	} else {
		frm.set_value('payment_status', 'Unpaid');
	}
}
