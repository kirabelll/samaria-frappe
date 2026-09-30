// Transporter Agreement — Client-side controller
// Frappe v15

frappe.ui.form.on("Transporter Agreement", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Deliveries"), function () {
				frappe.set_route("List", "Aggregate Delivery", { agreement: frm.doc.name });
			}, __("Links"));
		}
	}
});
