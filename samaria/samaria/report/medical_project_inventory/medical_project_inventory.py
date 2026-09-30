# -*- coding: utf-8 -*-
"""
Medical Project Inventory Report
Shows pharmaceutical batch inventory with FEFO valuation, expiry status, and stock levels.
Frappe v15
"""
import frappe
from frappe import _
from frappe.utils import flt, date_diff, nowdate


def execute(filters=None):
	columns = get_columns()
	data    = get_data(filters)
	chart   = get_chart_data(data)
	summary = get_report_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Batch ID"),            "fieldname": "name",          "fieldtype": "Link",     "options": "Medical Batch", "width": 130},
		{"label": _("Batch / Lot No"),       "fieldname": "batch_no",      "fieldtype": "Data",     "width": 120},
		{"label": _("Item Code"),            "fieldname": "item_code",     "fieldtype": "Link",     "options": "Item",          "width": 120},
		{"label": _("Item Name"),            "fieldname": "item_name",     "fieldtype": "Data",     "width": 200},
		{"label": _("Store"),                "fieldname": "warehouse",     "fieldtype": "Data",     "width": 120},
		{"label": _("Supplier"),             "fieldname": "supplier",      "fieldtype": "Link",     "options": "Supplier",      "width": 140},
		{"label": _("Current Qty"),          "fieldname": "quantity",      "fieldtype": "Float",    "width": 100},
		{"label": _("Cost Price (ETB)"),     "fieldname": "cost_price",    "fieldtype": "Currency", "width": 120},
		{"label": _("Total Value (ETB)"),    "fieldname": "total_value",   "fieldtype": "Currency", "width": 130},
		{"label": _("Expiry Date"),          "fieldname": "expiry_date",   "fieldtype": "Date",     "width": 100},
		{"label": _("Days to Expiry"),       "fieldname": "days_to_expiry","fieldtype": "Int",      "width": 110},
		{"label": _("Status"),               "fieldname": "status",        "fieldtype": "Data",     "width": 100},
	]


def get_data(filters=None):
	if not frappe.db.table_exists("tabMedical Batch"):
		return []

	conditions = ["1=1"]
	values = {}

	if filters:
		if filters.get("item_code"):
			conditions.append("item_code = %(item_code)s")
			values["item_code"] = filters["item_code"]
		if filters.get("warehouse"):
			conditions.append("warehouse = %(warehouse)s")
			values["warehouse"] = filters["warehouse"]
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters["status"]
		expiry_status = filters.get("expiry_status")
		if expiry_status == "Expired":
			conditions.append("expiry_date < %(today)s")
			values["today"] = nowdate()
		elif expiry_status == "Near Expiry (<90 Days)":
			conditions.append("expiry_date BETWEEN %(today)s AND DATE_ADD(%(today)s, INTERVAL 90 DAY)")
			values["today"] = nowdate()
		elif expiry_status == "Safe":
			conditions.append("expiry_date > DATE_ADD(%(today)s, INTERVAL 90 DAY)")
			values["today"] = nowdate()

	where = " AND ".join(conditions)
	rows = frappe.db.sql(f"""
		SELECT
			name, batch_no, item_code,
			COALESCE(item_name, item_code) AS item_name,
			COALESCE(warehouse, 'Medical Store') AS warehouse,
			supplier,
			COALESCE(quantity, 0)   AS quantity,
			COALESCE(cost_price, 0) AS cost_price,
			COALESCE(quantity, 0) * COALESCE(cost_price, 0) AS total_value,
			expiry_date, days_to_expiry, status
		FROM `tabMedical Batch`
		WHERE {where}
		ORDER BY expiry_date ASC, item_code ASC
	""", values, as_dict=True)

	# Re-calculate days_to_expiry live
	today = nowdate()
	for row in rows:
		if row.get("expiry_date"):
			row["days_to_expiry"] = date_diff(row["expiry_date"], today)
	return rows


def get_chart_data(data):
	if not data:
		return None
	status_counts = {}
	for row in data:
		s = row.get("status") or "Unknown"
		status_counts[s] = status_counts.get(s, 0) + 1

	return {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [{"values": list(status_counts.values())}]
		},
		"type": "donut",
		"colors": ["#10b981", "#f59e0b", "#ef4444", "#6b7280", "#8b5cf6", "#3b82f6"]
	}


def get_report_summary(data):
	if not data:
		return []
	total_batches   = len(data)
	total_value     = sum(flt(r.get("total_value")) for r in data)
	near_expiry     = sum(1 for r in data if 0 < (r.get("days_to_expiry") or 0) <= 90)
	expired_count   = sum(1 for r in data if (r.get("days_to_expiry") or 1) <= 0)
	return [
		{"value": total_batches,          "label": _("Total Batch Units"),     "datatype": "Int",      "indicator": "Blue"},
		{"value": round(total_value, 2),  "label": _("Inventory Value (ETB)"), "datatype": "Currency", "indicator": "Green"},
		{"value": near_expiry,            "label": _("Near Expiry (<90 Days)"), "datatype": "Int",     "indicator": "Orange"},
		{"value": expired_count,          "label": _("Expired Lots"),          "datatype": "Int",      "indicator": "Red"},
	]
