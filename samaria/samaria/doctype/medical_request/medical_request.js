// Medical Request — Client-side controller
// Frappe v15

frappe.ui.form.on("Medical Request", {
	refresh: function (frm) {
		if (!frm.is_new() && ["Submitted", "Quoted", "Approved"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Create Store Issue"), function () {
				frappe.call({
					method: "create_store_issue",
					doc: frm.doc,
					callback: function (r) {
						if (r.message) {
							frappe.show_alert({ message: __("Store Issue {0} created.", [r.message]), indicator: "green" });
							frappe.set_route("Form", "Medical Store Issue", r.message);
						}
					}
				});
			}, __("Actions"));
		}
	}
});

// Child table row calculations
frappe.ui.form.on("Medical Request Item", {
	qty:        (frm, cdt, cdn) => calc_row(frm, cdt, cdn),
	unit_price: (frm, cdt, cdn) => calc_row(frm, cdt, cdn),
	items_remove: (frm) => update_totals(frm)
});

function calc_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "total_amount", flt(row.qty) * flt(row.unit_price));
	update_totals(frm);
}

function update_totals(frm) {
	let count = 0, total = 0;
	(frm.doc.items || []).forEach(row => {
		count++;
		total += flt(row.total_amount);
	});
	frm.set_value("total_items_count", count);
	frm.set_value("total_amount", total);
}
