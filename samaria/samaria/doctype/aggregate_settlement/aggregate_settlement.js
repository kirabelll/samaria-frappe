// Aggregate Settlement — Client-side controller
// Frappe v15

frappe.ui.form.on("Aggregate Settlement", {
	refresh: function (frm) {
		if (frm.doc.docstatus === 0 && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Fetch Deliveries"), function () {
				frappe.call({
					method: "populate_deliveries",
					doc: frm.doc,
					callback: function (r) {
						if (r.message !== undefined) {
							frm.refresh_fields();
							frappe.show_alert({
								message: __("{0} delivery trip(s) loaded.", [r.message]),
								indicator: "green"
							});
						}
					}
				});
			}, __("Actions"));
		}
	},

	association_charge_enabled: (frm) => frm.trigger("recalculate_final"),
	association_rate: (frm) => frm.trigger("recalculate_final"),
	recovery_deduction: (frm) => frm.trigger("recalculate_final"),

	recalculate_final: function (frm) {
		const total_net = flt(frm.doc.total_net_payment);
		let assoc_amount = 0;
		if (frm.doc.association_charge_enabled && flt(frm.doc.association_rate) > 0) {
			assoc_amount = (flt(frm.doc.association_rate) / 100.0) * total_net;
		}
		frm.set_value("association_amount", assoc_amount);
		const final_payable = Math.max(0, total_net - assoc_amount - flt(frm.doc.recovery_deduction));
		frm.set_value("final_payable", final_payable);
	}
});

frappe.ui.form.on("Aggregate Settlement Item", {
	items_remove: (frm) => frm.trigger("recalculate_totals"),
	net_truck_payment: (frm) => frm.trigger("recalculate_totals"),

	recalculate_totals: function (frm) {
		let total_dispatches = 0, total_loaded = 0, total_delivered = 0,
			total_shortage = 0, total_gross = 0, total_deduct = 0, total_net = 0;

		(frm.doc.items || []).forEach(row => {
			total_dispatches++;
			total_loaded += flt(row.loaded_volume);
			total_delivered += flt(row.delivered_volume);
			total_shortage += flt(row.shortage_volume);
			total_gross += flt(row.gross_truck_fee);
			total_deduct += flt(row.shortage_deduction);
			total_net += flt(row.net_truck_payment);
		});

		frm.set_value("total_dispatches", total_dispatches);
		frm.set_value("total_loaded_volume", total_loaded);
		frm.set_value("total_delivered_volume", total_delivered);
		frm.set_value("total_shortage_volume", total_shortage);
		frm.set_value("total_gross_fee", total_gross);
		frm.set_value("total_shortage_deduction", total_deduct);
		frm.set_value("total_net_payment", total_net);
		frm.trigger("recalculate_final");
	}
});
