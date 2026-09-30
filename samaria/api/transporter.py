# -*- coding: utf-8 -*-
"""
Samaria Transporter API
Rate lookup, recovery balance, truck availability.
Frappe v15
"""
import frappe
from frappe.utils import flt, getdate, nowdate


@frappe.whitelist()
def get_active_rate(transporter, product_type=None, item_code=None):
	"""Find the current active Transporter Agreement rate for a transporter."""
	if not frappe.db.table_exists("tabTransporter Agreement"):
		return {}

	filters = {
		"transporter": transporter,
		"status": "Active",
		"valid_from": ["<=", nowdate()],
		"valid_to":   [">=", nowdate()]
	}
	if product_type:
		filters["product_type"] = product_type

	agreements = frappe.get_all(
		"Transporter Agreement",
		filters=filters,
		fields=["name", "association_service_charge_percent", "valid_from", "valid_to"],
		order_by="valid_from desc",
		limit=1
	)
	if not agreements:
		return {}

	agr = agreements[0]
	result = {
		"agreement":        agr.name,
		"valid_from":       str(agr.valid_from),
		"valid_to":         str(agr.valid_to),
		"association_pct":  flt(agr.association_service_charge_percent),
		"transport_rate":   None,
		"aggregate_value":  None
	}

	# Fetch per-item rate
	if item_code:
		item_rate = frappe.get_all(
			"Transporter Agreement Item",
			filters={"parent": agr.name, "item_code": item_code},
			fields=["transport_rate", "aggregate_value"],
			limit=1
		)
		if item_rate:
			result["transport_rate"]  = flt(item_rate[0].transport_rate)
			result["aggregate_value"] = flt(item_rate[0].aggregate_value)
	else:
		# Return first item row if no specific item requested
		all_items = frappe.get_all(
			"Transporter Agreement Item",
			filters={"parent": agr.name},
			fields=["item_code", "transport_rate", "aggregate_value"]
		)
		result["items"] = all_items

	return result


@frappe.whitelist()
def get_transporter_recovery_balance(transporter):
	"""Return open recovery claims total for a transporter."""
	if not frappe.db.table_exists("tabTransporter Recovery"):
		return {}

	rows = frappe.db.sql("""
		SELECT
			COALESCE(SUM(original_amount),  0) AS total_claims,
			COALESCE(SUM(recovered_amount), 0) AS total_recovered,
			COALESCE(SUM(pending_amount),   0) AS total_pending,
			COUNT(CASE WHEN status = 'Open'    THEN 1 END) AS open_count,
			COUNT(CASE WHEN status = 'Partial' THEN 1 END) AS partial_count
		FROM `tabTransporter Recovery`
		WHERE transporter = %(transporter)s AND status IN ('Open', 'Partial')
	""", {"transporter": transporter}, as_dict=True)

	if rows:
		r = rows[0]
		return {
			"total_claims":    round(flt(r.total_claims),    2),
			"total_recovered": round(flt(r.total_recovered), 2),
			"total_pending":   round(flt(r.total_pending),   2),
			"open_count":      r.open_count    or 0,
			"partial_count":   r.partial_count or 0
		}
	return {"total_claims": 0, "total_recovered": 0, "total_pending": 0, "open_count": 0, "partial_count": 0}


@frappe.whitelist()
def get_active_trucks(transporter=None):
	"""Return active trucks, optionally filtered by transporter."""
	if not frappe.db.table_exists("tabTruck"):
		return []

	filters = {"status": "Active"}
	if transporter:
		filters["transporter"] = transporter

	return frappe.get_all(
		"Truck",
		filters=filters,
		fields=["name", "plate_no", "transporter", "transporter_name",
				"truck_type", "capacity", "capacity_unit", "driver_name"],
		order_by="plate_no asc"
	)


@frappe.whitelist()
def get_transporter_summary(from_date=None, to_date=None):
	"""Return per-transporter performance summary across Aggregate Deliveries."""
	if not frappe.db.table_exists("tabAggregate Delivery"):
		return []

	conds = ["docstatus < 2"]
	vals  = {}
	if from_date:
		conds.append("dispatch_date >= %(from_date)s"); vals["from_date"] = from_date
	if to_date:
		conds.append("dispatch_date <= %(to_date)s");   vals["to_date"]   = to_date

	return frappe.db.sql(f"""
		SELECT
			COALESCE(transporter_name, transporter) AS transporter_name,
			COUNT(name)                              AS total_trips,
			COALESCE(SUM(loaded_volume),    0)       AS loaded_m3,
			COALESCE(SUM(delivered_volume), 0)       AS delivered_m3,
			COALESCE(SUM(shortage_volume),  0)       AS shortage_m3,
			COALESCE(SUM(net_truck_payment),0)       AS total_payment
		FROM `tabAggregate Delivery`
		WHERE {" AND ".join(conds)}
		GROUP BY transporter
		ORDER BY total_trips DESC
	""", vals, as_dict=True)
