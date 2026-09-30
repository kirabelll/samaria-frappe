// Truck — Client-side controller
// Frappe v15

frappe.ui.form.on("Truck", {
	plate_no: function (frm) {
		if (frm.doc.plate_no) {
			frm.set_value("plate_no", frm.doc.plate_no.toUpperCase().trim());
		}
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Deliveries"), function () {
				frappe.set_route("List", "Aggregate Delivery", { truck: frm.doc.name });
			}, __("Links"));
			frm.add_custom_button(__("View Liftings"), function () {
				frappe.set_route("List", "Cement Lifting", { truck: frm.doc.name });
			}, __("Links"));
		}
	}
});
