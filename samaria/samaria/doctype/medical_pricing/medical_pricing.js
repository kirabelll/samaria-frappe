frappe.ui.form.on('MedicalPricing', {
	manufacturer_price: function(frm) { frm.trigger('recalculate_pricing'); },
	freight: function(frm) { frm.trigger('recalculate_pricing'); },
	insurance: function(frm) { frm.trigger('recalculate_pricing'); },
	customs: function(frm) { frm.trigger('recalculate_pricing'); },
	inland_transport: function(frm) { frm.trigger('recalculate_pricing'); },
	bank_cost: function(frm) { frm.trigger('recalculate_pricing'); },
	warehouse_cost: function(frm) { frm.trigger('recalculate_pricing'); },
	handling_cost: function(frm) { frm.trigger('recalculate_pricing'); },
	wastage_allowance: function(frm) { frm.trigger('recalculate_pricing'); },
	other_costs: function(frm) { frm.trigger('recalculate_pricing'); },
	margin_percent: function(frm) { frm.trigger('recalculate_pricing'); },
	recalculate_pricing: function(frm) {
		var total = flt(frm.doc.manufacturer_price) +
			flt(frm.doc.freight) +
			flt(frm.doc.insurance) +
			flt(frm.doc.customs) +
			flt(frm.doc.inland_transport) +
			flt(frm.doc.bank_cost) +
			flt(frm.doc.warehouse_cost) +
			flt(frm.doc.handling_cost) +
			flt(frm.doc.wastage_allowance) +
			flt(frm.doc.other_costs);

		frm.set_value('total_cost', total);

		var margin = flt(frm.doc.margin_percent);
		var rec_price = total > 0 ? total * (1.0 + margin / 100.0) : 0;
		frm.set_value('recommended_price', rec_price);
		if (!frm.doc.approved_price) {
			frm.set_value('approved_price', rec_price);
		}
	}
});
