# -*- coding: utf-8 -*-
"""
Medical Project Inventory Report
Tracks pharmaceutical batches across warehouse lots, shelf-life, expiry countdown, and valuation.
Frappe Framework Version-16
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate, date_diff


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": _("Batch ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Medical Batch",
			"width": 130
		},
		{
			"label": _("Batch / Lot No"),
			"fieldname": "batch_no",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Medical Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 140
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 140
		},
		{
			"label": _("Current Qty"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Cost Price (ETB)"),
			"fieldname": "cost_price",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Total Valuation (ETB)"),
			"fieldname": "total_value",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Expiry Date"),
			"fieldname": "expiry_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Days to Expiry"),
			"fieldname": "days_to_expiry",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 110
		}
	]


def get_data(filters=None):
	if not frappe.db.table_exists("Medical Batch"):
		return []

	conditions = []
	values = {}

	if filters:
		if filters.get("item_code"):
			conditions.append("item_code = %(item_code)s")
			values["item_code"] = filters.get("item_code")
		if filters.get("warehouse"):
			conditions.append("warehouse = %(warehouse)s")
			values["warehouse"] = filters.get("warehouse")
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters.get("status")
		if filters.get("expiry_status"):
			if filters.get("expiry_status") == "Expired":
				conditions.append("expiry_date < %(today)s")
				values["today"] = nowdate()
			elif filters.get("expiry_status") == "Near Expiry (<90 Days)":
				conditions.append("expiry_date >= %(today)s AND expiry_date <= DATE_ADD(%(today)s, INTERVAL 90 DAY)")
				values["today"] = nowdate()
			elif filters.get("expiry_status") == "Safe":
				conditions.append("expiry_date > DATE_ADD(%(today)s, INTERVAL 90 DAY)")
				values["today"] = nowdate()

	where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

	raw_data = frappe.db.sql(f"""
		SELECT
			name,
			batch_no,
			item_code,
			item_name,
			warehouse,
			supplier,
			quantity,
			cost_price,
			(quantity * cost_price) as total_value,
			expiry_date,
			days_to_expiry,
			status
		FROM `tabMedical Batch`
		{where_clause}
		ORDER BY expiry_date ASC, creation DESC
	""", values, as_dict=True)

	today = nowdate()
	for row in raw_data:
		if row.get("expiry_date"):
			row["days_to_expiry"] = date_diff(row.get("expiry_date"), today)

	return raw_data


def get_chart_data(data):
	if not data:
		return None

	status_counts = {}
	for row in data:
		st = row.get("status") or _("Available")
		status_counts[st] = status_counts.get(st, 0) + 1

	labels = list(status_counts.keys())
	values = list(status_counts.values())

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Batches"), "values": values}]
		},
		"type": "donut",
		"colors": ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"]
	}


def get_report_summary(data):
	if not data:
		return []

	total_qty = sum(flt(r.get("quantity", 0)) for r in data)
	total_value = sum(flt(r.get("total_value", 0)) for r in data)
	near_expiry_count = sum(1 for r in data if 0 <= flt(r.get("days_to_expiry", 999)) <= 90)
	expired_count = sum(1 for r in data if flt(r.get("days_to_expiry", 999)) < 0)

	return [
		{
			"value": round(total_qty, 0),
			"label": _("Total Batch Units"),
			"datatype": "Float",
			"indicator": "Blue"
		},
		{
			"value": round(total_value, 2),
			"label": _("Total Inventory Value (ETB)"),
			"datatype": "Currency",
			"indicator": "Green"
		},
		{
			"value": near_expiry_count,
			"label": _("Near Expiry (<90 Days)"),
			"datatype": "Int",
			"indicator": "Orange"
		},
		{
			"value": expired_count,
			"label": _("Expired Lots"),
			"datatype": "Int",
			"indicator": "Red"
		}
	]
