frappe.ui.form.on('Cement Lifting', {
	factory_weight: function(frm) {
		calculate_shortage(frm);
	},
	buyer_weighbridge_qty: function(frm) {
		calculate_shortage(frm);
	}
});

function calculate_shortage(frm) {
	let factoryWt = flt(frm.doc.factory_weight);
	let buyerWt = frm.doc.buyer_weighbridge_qty !== '' && frm.doc.buyer_weighbridge_qty !== null && frm.doc.buyer_weighbridge_qty !== undefined
		? flt(frm.doc.buyer_weighbridge_qty)
		: factoryWt;
	let shortage = Math.max(0, factoryWt - buyerWt);
	frm.set_value('shortage_qty', shortage);
}
