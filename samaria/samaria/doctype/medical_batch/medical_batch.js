// Medical Batch — Client-side controller
// Frappe v15

frappe.ui.form.on("Medical Batch", {
	expiry_date: function (frm) {
		if (frm.doc.expiry_date) {
			const today = frappe.datetime.get_today();
			const days  = frappe.datetime.get_diff(frm.doc.expiry_date, today);
			frm.set_value("days_to_expiry", days);
			if (days <= 0) {
				frm.set_value("status", "Expired");
				frappe.show_alert({ message: __("This batch has expired."), indicator: "red" });
			} else if (days <= 90) {
				frappe.show_alert({ message: __("Warning: Batch expires in {0} days.", [days]), indicator: "orange" });
			}
		}
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			const days = flt(frm.doc.days_to_expiry);
			if (days > 0 && days <= 90) {
				frm.dashboard.add_comment(__("Near Expiry: {0} days remaining.", [days]), "orange");
			} else if (days <= 0) {
				frm.dashboard.add_comment(__("This batch has EXPIRED."), "red");
			}
		}
	}
});
