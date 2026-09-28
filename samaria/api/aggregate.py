# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def get_unsettled_deliveries(transporter, from_date=None, to_date=None):
	"""
	Fetch all submitted, delivered or verified Aggregate Deliveries
	for a given transporter that have not been settled yet.
	"""
	filters = {
		"transporter": transporter,
		"docstatus": 1,
		"status": ["in", ["Dispatched", "Delivered", "Verified"]]
	}

	if from_date and to_date:
		filters["dispatch_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["dispatch_date"] = [">=", from_date]
	elif to_date:
		filters["dispatch_date"] = ["<=", to_date]

	deliveries = frappe.get_all(
		"Aggregate Delivery",
		filters=filters,
		fields=[
			"name",
			"dispatch_date",
			"truck",
			"customer",
			"supplier",
			"item_name",
			"loaded_volume",
			"delivered_volume",
			"shortage_volume",
			"transport_rate",
			"aggregate_value",
			"gross_truck_fee",
			"shortage_deduction",
			"net_truck_payment",
			"status"
		],
		order_by="dispatch_date asc"
	)
	return deliveries


@frappe.whitelist()
def get_aggregate_analytics():
	"""
	Summary statistics for the Aggregate dashboard.
	"""
	total_dispatches = frappe.db.count("Aggregate Delivery", {"docstatus": 1})
	total_volume = frappe.db.sql("""
		SELECT 
			COALESCE(SUM(loaded_volume), 0) as total_loaded,
			COALESCE(SUM(delivered_volume), 0) as total_delivered,
			COALESCE(SUM(shortage_volume), 0) as total_shortage,
			COALESCE(SUM(net_truck_payment), 0) as total_paid
		FROM `tabAggregate Delivery`
		WHERE docstatus = 1
	""", as_dict=True)[0]

	return {
		"total_dispatches": total_dispatches,
		"total_loaded_volume": flt(total_volume.total_loaded, 2),
		"total_delivered_volume": flt(total_volume.total_delivered, 2),
		"total_shortage": flt(total_volume.total_shortage, 2),
		"total_paid_transport": flt(total_volume.total_paid, 2)
	}
