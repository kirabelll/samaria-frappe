frappe.ui.form.on('AggregateSettlement', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.status === 'Draft') {
			frm.add_custom_button(__('Fetch Deliveries'), function() {
				frm.call({
					doc: frm.doc,
					method: 'populate_deliveries',
					freeze: true,
					freeze_message: __('Fetching un-settled dispatches...'),
					callback: function(r) {
						frm.refresh_fields();
						frappe.msgprint(__('Loaded {0} dispatches.', [r.message || 0]));
					}
				});
			}, __('Actions'));
		}
	},
	association_charge_enabled: function(frm) {
		frm.trigger('recalculate_summary');
	},
	association_rate: function(frm) {
		frm.trigger('recalculate_summary');
	},
	recovery_deduction: function(frm) {
		frm.trigger('recalculate_summary');
	},
	recalculate_summary: function(frm) {
		var total_net = flt(frm.doc.total_net_payment);
		var assoc_amt = 0;
		if (frm.doc.association_charge_enabled && flt(frm.doc.association_rate) > 0) {
			assoc_amt = (flt(frm.doc.association_rate) / 100.0) * total_net;
		}
		var recovery = flt(frm.doc.recovery_deduction);
		var final_pay = Math.max(0, total_net - assoc_amt - recovery);

		frm.set_value('association_amount', assoc_amt);
		frm.set_value('final_payable', final_pay);
	}
});
