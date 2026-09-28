// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cement Lifting', {
	setup: function(frm) {
		frm.set_query('coupon', function() {
			if (frm.doc.factory) {
				return {
					filters: {
						factory: frm.doc.factory,
						status: ['in', ['Handed Over', 'Collected', 'In Custody']]
					}
				};
			}
		});

		frm.set_query('cement_purchase', function() {
			if (frm.doc.factory) {
				return {
					filters: {
						factory: frm.doc.factory,
						status: 'Active'
					}
				};
			}
		});
	},
	factory_weight: function(frm) {
		calculate_cement_shortage(frm);
	},
	buyer_weighbridge_qty: function(frm) {
		calculate_cement_shortage(frm);
	},
	penalty_rate_per_ton: function(frm) {
		calculate_cement_shortage(frm);
	}
});

function calculate_cement_shortage(frm) {
	let fac = flt(frm.doc.factory_weight);
	let buyer = frm.doc.buyer_weighbridge_qty ? flt(frm.doc.buyer_weighbridge_qty) : fac;
	let rate = flt(frm.doc.penalty_rate_per_ton);

	let shortage = 0;
	if (frm.doc.buyer_weighbridge_qty) {
		shortage = Math.max(0, fac - buyer);
	}
	let penalty = shortage * rate;

	frm.set_value('shortage_qty', shortage);
	frm.set_value('shortage_penalty', penalty);
}
