frappe.ui.form.on('MedicalRequest', {
	refresh: function(frm) {
		if (!frm.is_new() && ['Submitted', 'Quoted', 'Approved'].includes(frm.doc.status)) {
			frm.add_custom_button(__('Create Store Issue'), function() {
				frm.call({
					doc: frm.doc,
					method: 'create_store_issue',
					freeze: true,
					freeze_message: __('Generating Store Issue...'),
					callback: function(r) {
						if (r.message) {
							frappe.set_route('Form', 'Medical Store Issue', r.message);
						}
					}
				});
			}, __('Create'));
		}
	}
});

frappe.ui.form.on('MedicalRequestItem', {
	qty: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.total_amount = flt(row.qty) * flt(row.unit_price);
		frm.refresh_field('items');
		recalc_request_totals(frm);
	},
	unit_price: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.total_amount = flt(row.qty) * flt(row.unit_price);
		frm.refresh_field('items');
		recalc_request_totals(frm);
	},
	items_remove: function(frm) {
		recalc_request_totals(frm);
	}
});

function recalc_request_totals(frm) {
	var total = 0;
	var count = 0;
	(frm.doc.items || []).forEach(function(row) {
		count += 1;
		total += flt(row.total_amount);
	});
	frm.set_value('total_items_count', count);
	frm.set_value('total_amount', total);
}
