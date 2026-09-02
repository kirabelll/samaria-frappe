frappe.ui.form.on('Aggregate Settlement', {
	commission_rate: function(frm) {
		let net = flt(frm.doc.total_net_payment);
		let rate = flt(frm.doc.commission_rate);
		let commAmt = (rate / 100.0) * net;
		frm.set_value('commission_amount', commAmt);
		frm.set_value('final_payable', net - commAmt);
	}
});
