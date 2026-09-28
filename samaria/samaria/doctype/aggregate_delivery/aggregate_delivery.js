frappe.ui.form.on('AggregateDelivery', {
	loaded_volume: function(frm) {
		frm.trigger('calculate_totals');
	},
	delivered_volume: function(frm) {
		frm.trigger('calculate_totals');
	},
	transport_rate: function(frm) {
		frm.trigger('calculate_totals');
	},
	aggregate_value: function(frm) {
		frm.trigger('calculate_totals');
	},
	customer_price: function(frm) {
		frm.trigger('calculate_totals');
	},
	truck: function(frm) {
		if (frm.doc.truck) {
			frappe.db.get_value('Truck', frm.doc.truck, 'capacity', function(val) {
				if (val && val.capacity) {
					frm.set_value('truck_capacity', val.capacity);
					frm.trigger('calculate_totals');
				}
			});
		}
	},
	calculate_totals: function(frm) {
		var loaded = flt(frm.doc.loaded_volume);
		var delivered = frm.doc.delivered_volume !== undefined && frm.doc.delivered_volume !== null && frm.doc.delivered_volume !== "" 
			? flt(frm.doc.delivered_volume) 
			: loaded;
		var rate = flt(frm.doc.transport_rate);
		var supp_rate = flt(frm.doc.aggregate_value);
		var cust_rate = flt(frm.doc.customer_price) || supp_rate;
		var capacity = flt(frm.doc.truck_capacity);

		var billable = (capacity > 0 && loaded > capacity) ? capacity : loaded;
		frm.set_value('billable_volume', billable);

		var shortage = (frm.doc.delivered_volume !== undefined && frm.doc.delivered_volume !== null && frm.doc.delivered_volume !== "") 
			? Math.max(0, loaded - delivered) 
			: 0;
		frm.set_value('shortage_volume', shortage);

		var gross = billable * rate;
		var shortage_ded = shortage * supp_rate;
		var net_truck = Math.max(0, gross - shortage_ded);

		var cust_rec = loaded * cust_rate;
		var supp_pay = delivered * supp_rate;
		var profit = cust_rec - supp_pay - gross;

		frm.set_value('gross_truck_fee', gross);
		frm.set_value('shortage_deduction', shortage_ded);
		frm.set_value('net_truck_payment', net_truck);
		frm.set_value('customer_receivable', cust_rec);
		frm.set_value('supplier_payable', supp_pay);
		frm.set_value('net_profit_amount', profit);
	}
});
