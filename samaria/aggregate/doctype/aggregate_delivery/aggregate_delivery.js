// Copyright (c) 2026, Samaria ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Aggregate Delivery', {
	setup: function(frm) {
		frm.set_query('truck', function() {
			if (frm.doc.transporter) {
				return {
					filters: {
						transporter: frm.doc.transporter,
						status: 'Active'
					}
				};
			}
		});
	},
	transporter: function(frm) {
		if (frm.doc.transporter) {
			// Auto fetch active agreement
			frappe.db.get_list('Transporter Agreement', {
				filters: {
					transporter: frm.doc.transporter,
					product_type: 'Aggregate',
					status: 'Active'
				},
				fields: ['name']
			}).then(records => {
				if (records.length > 0) {
					frm.set_value('agreement', records[0].name);
				}
			});
		}
	},
	loaded_volume: function(frm) {
		calculate_aggregate_pricing(frm);
	},
	delivered_volume: function(frm) {
		calculate_aggregate_pricing(frm);
	},
	transport_rate: function(frm) {
		calculate_aggregate_pricing(frm);
	},
	aggregate_value: function(frm) {
		calculate_aggregate_pricing(frm);
	}
});

function calculate_aggregate_pricing(frm) {
	let loaded = flt(frm.doc.loaded_volume);
	let delivered = frm.doc.delivered_volume !== undefined && frm.doc.delivered_volume !== null && frm.doc.delivered_volume !== '' ? flt(frm.doc.delivered_volume) : loaded;
	let rate = flt(frm.doc.transport_rate);
	let agg_val = flt(frm.doc.aggregate_value);

	let shortage = 0;
	let gross = 0;
	if (frm.doc.delivered_volume) {
		shortage = Math.max(0, loaded - delivered);
		gross = delivered * rate;
	} else {
		gross = loaded * rate;
	}

	let shortage_deduction = shortage * agg_val;
	let net = Math.max(0, gross - shortage_deduction);

	frm.set_value('shortage_volume', shortage);
	frm.set_value('gross_truck_fee', gross);
	frm.set_value('shortage_deduction', shortage_deduction);
	frm.set_value('net_truck_payment', net);
}
