// Aggregate Delivery — Client-side controller
// Frappe v15

frappe.ui.form.on("Aggregate Delivery", {
	// Trigger recalculation on any financial field change
	loaded_volume: (frm) => frm.trigger("calculate_financials"),
	delivered_volume: (frm) => frm.trigger("calculate_financials"),
	transport_rate: (frm) => frm.trigger("calculate_financials"),
	aggregate_value: (frm) => frm.trigger("calculate_financials"),
	customer_price: (frm) => frm.trigger("calculate_financials"),

	truck: function (frm) {
		if (frm.doc.truck) {
			frappe.db.get_value("Truck", frm.doc.truck, "capacity", (r) => {
				if (r && r.capacity) {
					frm.set_value("truck_capacity", r.capacity);
					frm.trigger("calculate_financials");
				}
			});
		}
	},

	calculate_financials: function (frm) {
		const loaded = flt(frm.doc.loaded_volume);
		const delivered = frm.doc.delivered_volume !== undefined && frm.doc.delivered_volume !== null
			? flt(frm.doc.delivered_volume) : loaded;
		const rate = flt(frm.doc.transport_rate);
		const supp_rate = flt(frm.doc.aggregate_value);
		const cust_rate = flt(frm.doc.customer_price) || supp_rate;
		const capacity = flt(frm.doc.truck_capacity);

		// Billable volume
		const billable = (capacity > 0 && loaded > capacity) ? capacity : loaded;
		frm.set_value("billable_volume", billable);

		// Shortage
		const shortage = (frm.doc.delivered_volume !== undefined && frm.doc.delivered_volume !== null)
			? Math.max(0, loaded - delivered) : 0;
		frm.set_value("shortage_volume", shortage);

		// Transport fees
		const gross = billable * rate;
		const deduction = shortage * supp_rate;
		const net_transport = Math.max(0, gross - deduction);
		frm.set_value("gross_truck_fee", gross);
		frm.set_value("shortage_deduction", deduction);
		frm.set_value("net_truck_payment", net_transport);

		// Commercial amounts
		const cust_receivable = loaded * cust_rate;
		const supp_payable = delivered * supp_rate;
		const profit = cust_receivable - supp_payable - gross;
		frm.set_value("customer_receivable", cust_receivable);
		frm.set_value("supplier_payable", supp_payable);
		frm.set_value("net_profit_amount", profit);

		// Auto-advance status
		if (frm.doc.delivered_volume && frm.doc.status === "Dispatched") {
			frm.set_value("status", "Delivered");
		}
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Settlement"), function () {
				frappe.set_route("List", "Aggregate Settlement", {
					transporter: frm.doc.transporter
				});
			}, __("Links"));
		}
	}
});
