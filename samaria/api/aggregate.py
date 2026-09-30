# -*- coding: utf-8 -*-
"""
Samaria Aggregate API
Exposes aggregate delivery and settlement query endpoints.
Frappe v15
"""
import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_unsettled_deliveries(transporter, from_date=None, to_date=None):
	"""Return submitted, un-settled Aggregate Deliveries for a transporter."""
	filters = {
		"transporter": transporter,
		"status": ["in", ["Dispatched", "Delivered", "Verified"]],
		"docstatus": 1
	}
	if from_date and to_date:
		filters["dispatch_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["dispatch_date"] = [">=", from_date]
	elif to_date:
		filters["dispatch_date"] = ["<=", to_date]

	return frappe.get_all(
		"Aggregate Delivery",
		filters=filters,
		fields=[
			"name", "dispatch_date", "pad_number", "truck",
			"customer", "customer_name",
			"loaded_volume", "delivered_volume", "shortage_volume",
			"transport_rate", "aggregate_value", "customer_price",
			"gross_truck_fee", "shortage_deduction", "net_truck_payment",
			"customer_receivable", "supplier_payable", "net_profit_amount",
			"status"
		],
		order_by="dispatch_date asc"
	)


@frappe.whitelist()
def get_aggregate_analytics(customer=None, from_date=None, to_date=None):
	"""Return aggregate summary statistics."""
	if not frappe.db.table_exists("tabAggregate Delivery"):
		return {}

	conds = ["docstatus < 2"]
	vals  = {}
	if customer:
		conds.append("customer = %(customer)s"); vals["customer"] = customer
	if from_date:
		conds.append("dispatch_date >= %(from_date)s"); vals["from_date"] = from_date
	if to_date:
		conds.append("dispatch_date <= %(to_date)s");   vals["to_date"]   = to_date

	result = frappe.db.sql(f"""
		SELECT
			COUNT(name)                          AS total_dispatches,
			COALESCE(SUM(loaded_volume),    0)   AS total_loaded,
			COALESCE(SUM(delivered_volume), 0)   AS total_delivered,
			COALESCE(SUM(shortage_volume),  0)   AS total_shortage,
			COALESCE(SUM(net_truck_payment),0)   AS total_net_transport,
			COALESCE(SUM(net_profit_amount),0)   AS total_net_profit
		FROM `tabAggregate Delivery`
		WHERE {" AND ".join(conds)}
	""", vals, as_dict=True)

	if result:
		r = result[0]
		return {
			"total_dispatches":    r.total_dispatches or 0,
			"total_loaded_m3":     round(flt(r.total_loaded),    1),
			"total_delivered_m3":  round(flt(r.total_delivered), 1),
			"total_shortage_m3":   round(flt(r.total_shortage),  1),
			"total_net_transport": round(flt(r.total_net_transport), 2),
			"total_net_profit":    round(flt(r.total_net_profit),    2),
		}
	return {}


@frappe.whitelist()
def get_deliveries_by_transporter(from_date=None, to_date=None):
	"""Return delivery counts and totals grouped by transporter."""
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
			COALESCE(SUM(delivered_volume), 0)       AS delivered_m3,
			COALESCE(SUM(net_truck_payment), 0)      AS total_payment
		FROM `tabAggregate Delivery`
		WHERE {" AND ".join(conds)}
		GROUP BY transporter
		ORDER BY total_trips DESC
	""", vals, as_dict=True)
