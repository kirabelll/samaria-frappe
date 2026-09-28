# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today

@frappe.whitelist()
def get_active_rate(transporter, product_type="Aggregate", item_code=None):
	"""
	Lookup agreed rate for a transporter and item from active agreement.
	"""
	agreement = frappe.db.get_value(
		"Transporter Agreement",
		{
			"transporter": transporter,
			"product_type": product_type,
			"status": "Active",
			"valid_from": ["<=", today()],
			"valid_to": [">=", today()]
		},
		"name"
	)
	if not agreement:
		return None

	agreement_doc = frappe.get_doc("Transporter Agreement", agreement)
	
	if item_code:
		for row in agreement_doc.agreement_items:
			if row.item_code == item_code:
				return {
					"agreement": agreement,
					"transport_rate": row.transport_rate,
					"aggregate_value": row.aggregate_value,
					"association_charge_enabled": agreement_doc.association_charge_enabled,
					"association_service_charge": agreement_doc.association_service_charge
				}

	return {
		"agreement": agreement,
		"association_charge_enabled": agreement_doc.association_charge_enabled,
		"association_service_charge": agreement_doc.association_service_charge
	}


@frappe.whitelist()
def get_transporter_recovery_balance(transporter):
	"""
	Returns outstanding pending claims/recoveries against a transporter.
	"""
	data = frappe.db.sql("""
		SELECT 
			COALESCE(SUM(original_amount), 0) as total_claims,
			COALESCE(SUM(recovered_amount), 0) as total_recovered,
			COALESCE(SUM(pending_amount), 0) as total_pending
		FROM `tabTransporter Recovery`
		WHERE transporter = %s AND status in ('Open', 'Partially Recovered')
	""", (transporter,), as_dict=True)[0]

	return {
		"total_claims": flt(data.total_claims, 2),
		"total_recovered": flt(data.total_recovered, 2),
		"total_pending": flt(data.total_pending, 2)
	}
