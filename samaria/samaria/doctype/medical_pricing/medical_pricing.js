frappe.ui.form.on('Medical Pricing', {
	manufacturer_price: function(frm) {
		calculate_landing_cost(frm);
	},
	freight: function(frm) {
		calculate_landing_cost(frm);
	},
	insurance: function(frm) {
		calculate_landing_cost(frm);
	},
	customs: function(frm) {
		calculate_landing_cost(frm);
	},
	inland_transport: function(frm) {
		calculate_landing_cost(frm);
	},
	bank_cost: function(frm) {
		calculate_landing_cost(frm);
	},
	warehouse_cost: function(frm) {
		calculate_landing_cost(frm);
	},
	handling_cost: function(frm) {
		calculate_landing_cost(frm);
	},
	wastage_allowance: function(frm) {
		calculate_landing_cost(frm);
	},
	other_costs: function(frm) {
		calculate_landing_cost(frm);
	},
	margin_percent: function(frm) {
		calculate_landing_cost(frm);
	}
});

function calculate_landing_cost(frm) {
	let totalCost = flt(frm.doc.manufacturer_price) +
		flt(frm.doc.freight) +
		flt(frm.doc.insurance) +
		flt(frm.doc.customs) +
		flt(frm.doc.inland_transport) +
		flt(frm.doc.bank_cost) +
		flt(frm.doc.warehouse_cost) +
		flt(frm.doc.handling_cost) +
		flt(frm.doc.wastage_allowance) +
		flt(frm.doc.other_costs);

	frm.set_value('total_cost', totalCost);

	let margin = flt(frm.doc.margin_percent);
	let recPrice = totalCost * (1.0 + margin / 100.0);
	frm.set_value('recommended_price', recPrice);

	if (!frm.doc.approved_price) {
		frm.set_value('approved_price', recPrice);
	}
}
