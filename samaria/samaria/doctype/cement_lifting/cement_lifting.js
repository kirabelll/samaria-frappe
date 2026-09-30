// Cement Lifting — Client-side controller
// Frappe v15

frappe.ui.form.on("Cement Lifting", {
	factory_weight:       (frm) => frm.trigger("calc_shortage"),
	buyer_weighbridge_qty: (frm) => frm.trigger("calc_shortage"),

	self_transport: function (frm) {
		frm.set_df_property("truck",           "reqd", !frm.doc.self_transport ? 1 : 0);
		frm.set_df_property("self_plate_no",   "reqd", frm.doc.self_transport  ? 1 : 0);
		frm.set_df_property("self_driver_name","reqd", frm.doc.self_transport  ? 1 : 0);
		frm.refresh_fields(["truck", "self_plate_no", "self_driver_name"]);
	},

	calc_shortage: function (frm) {
		const fac = flt(frm.doc.factory_weight);
		const buy = (frm.doc.buyer_weighbridge_qty !== null && frm.doc.buyer_weighbridge_qty !== undefined)
			? flt(frm.doc.buyer_weighbridge_qty) : fac;
		const short = Math.max(0, fac - buy);
		frm.set_value("shortage_qty", short);
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Purchase"), function () {
				frappe.set_route("Form", "Cement Purchase", frm.doc.purchase);
			}, __("Links"));

			if (frm.doc.coupon) {
				frm.add_custom_button(__("View Coupon"), function () {
					frappe.set_route("Form", "Cement Coupon", frm.doc.coupon);
				}, __("Links"));
			}
		}
	}
});
