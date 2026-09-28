// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Pricing', {
	manufacturer_price: function(frm) { calculate_pricing(frm); },
	freight: function(frm) { calculate_pricing(frm); },
	insurance: function(frm) { calculate_pricing(frm); },
	customs: function(frm) { calculate_pricing(frm); },
	inland_transport: function(frm) { calculate_pricing(frm); },
	bank_cost: function(frm) { calculate_pricing(frm); },
	warehouse_cost: function(frm) { calculate_pricing(frm); },
	handling_cost: function(frm) { calculate_pricing(frm); },
	wastage_allowance: function(frm) { calculate_pricing(frm); },
	other_costs: function(frm) { calculate_pricing(frm); },
	margin_percent: function(frm) { calculate_pricing(frm); }
});

function calculate_pricing(frm) {
	let cost = flt(frm.doc.manufacturer_price) +
		flt(frm.doc.freight) +
		flt(frm.doc.insurance) +
		flt(frm.doc.customs) +
		flt(frm.doc.inland_transport) +
		flt(frm.doc.bank_cost) +
		flt(frm.doc.warehouse_cost) +
		flt(frm.doc.handling_cost) +
		flt(frm.doc.wastage_allowance) +
		flt(frm.doc.other_costs);

	let margin = flt(frm.doc.margin_percent);
	let rec = cost * (1 + margin / 100);

	frm.set_value('total_cost', cost);
	frm.set_value('recommended_price', rec);
	if (!frm.doc.approved_price) {
		frm.set_value('approved_price', rec);
	}
}
