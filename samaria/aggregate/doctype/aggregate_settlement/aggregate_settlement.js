// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Aggregate Settlement', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.transporter) {
			frm.add_custom_button(__('Fetch Deliveries'), function() {
				frappe.call({
					method: 'samaria.api.aggregate.get_unsettled_deliveries',
					args: {
						transporter: frm.doc.transporter,
						from_date: frm.doc.period_from,
						to_date: frm.doc.period_to
					},
					callback: function(r) {
						if (r.message && r.message.length > 0) {
							frm.clear_table('deliveries');
							r.message.forEach(item => {
								let row = frm.add_child('deliveries');
								row.delivery = item.name;
								row.dispatch_date = item.dispatch_date;
								row.truck = item.truck;
								row.loaded_volume = item.loaded_volume;
								row.delivered_volume = item.delivered_volume || item.loaded_volume;
								row.shortage_volume = item.shortage_volume || 0;
								row.gross_fee = item.gross_truck_fee || 0;
								row.shortage_deduction = item.shortage_deduction || 0;
								row.net_payment = item.net_truck_payment || 0;
							});
							frm.refresh_field('deliveries');
							frm.save();
						} else {
							frappe.msgprint(__('No unsettled deliveries found for this transporter in the selected period.'));
						}
					}
				});
			}, __('Actions'));
		}
	},
	association_rate: function(frm) {
		calculate_final_payable(frm);
	},
	recovery_deduction: function(frm) {
		calculate_final_payable(frm);
	}
});

function calculate_final_payable(frm) {
	let net = flt(frm.doc.total_net_payment);
	let rate = flt(frm.doc.association_rate);
	let assoc_amount = (rate > 0) ? (net * rate / 100) : 0;
	frm.set_value('association_amount', assoc_amount);

	let rec = flt(frm.doc.recovery_deduction);
	frm.set_value('final_payable', Math.max(0, net - assoc_amount - rec));
}
