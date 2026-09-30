// Medical Pricing — Client-side controller
// Frappe v15

const COST_FIELDS = [
	"manufacturer_price", "freight", "insurance", "customs",
	"inland_transport", "bank_cost", "warehouse_cost",
	"handling_cost", "wastage_allowance", "other_costs"
];

const recalc_handler = (frm) => frm.trigger("recalculate_price");

COST_FIELDS.forEach(f => frappe.ui.form.on("Medical Pricing", { [f]: recalc_handler }));

frappe.ui.form.on("Medical Pricing", {
	margin_percent: recalc_handler,

	recalculate_price: function (frm) {
		const total_cost = COST_FIELDS.reduce((sum, f) => sum + flt(frm.doc[f]), 0);
		frm.set_value("total_cost", total_cost);
		const margin = flt(frm.doc.margin_percent) / 100.0;
		const recommended = total_cost * (1 + margin);
		frm.set_value("recommended_price", recommended);
		if (!flt(frm.doc.approved_price)) {
			frm.set_value("approved_price", recommended);
		}
	}
});
