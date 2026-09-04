frappe.ui.form.on('Aggregate Delivery', {
	loaded_volume: function(frm) {
		calculate_delivery_totals(frm);
	},
	delivered_volume: function(frm) {
		calculate_delivery_totals(frm);
	},
	transport_rate: function(frm) {
		calculate_delivery_totals(frm);
	},
	aggregate_value: function(frm) {
		calculate_delivery_totals(frm);
	},
	customer_price: function(frm) {
		calculate_delivery_totals(frm);
	}
});

function calculate_delivery_totals(frm) {
	let loaded = flt(frm.doc.loaded_volume);
	let delivered = frm.doc.delivered_volume !== '' && frm.doc.delivered_volume !== null && frm.doc.delivered_volume !== undefined 
		? flt(frm.doc.delivered_volume) 
		: loaded;
	let rate = flt(frm.doc.transport_rate);
	let suppRate = flt(frm.doc.aggregate_value);
	let custRate = frm.doc.customer_price ? flt(frm.doc.customer_price) : suppRate;
	let capacity = flt(frm.doc.truck_capacity);

	let billable = (capacity > 0 && loaded > capacity) ? capacity : loaded;
	let shortage = Math.max(0, loaded - delivered);
	let grossFee = billable * rate;
	let shortageDeduction = shortage * suppRate;
	let netPayment = Math.max(0, grossFee - shortageDeduction);

	let custReceivable = loaded * custRate;
	let suppPayable = delivered * suppRate;
	let netProfit = custReceivable - suppPayable - grossFee;

	frm.set_value('shortage_volume', shortage);
	frm.set_value('gross_truck_fee', grossFee);
	frm.set_value('shortage_deduction', shortageDeduction);
	frm.set_value('net_truck_payment', netPayment);
	frm.set_value('customer_receivable', custReceivable);
	frm.set_value('supplier_payable', suppPayable);
	frm.set_value('net_profit_amount', netProfit);
}
