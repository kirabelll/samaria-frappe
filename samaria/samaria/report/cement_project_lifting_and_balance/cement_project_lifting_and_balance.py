# -*- coding: utf-8 -*-
"""
Cement Project Lifting and Balance Report
Tracks factory purchases, liftings allocated to client projects, weighbridge variances, and penalties.
Frappe Framework Version-16
"""
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": _("Lifting ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Cement Lifting",
			"width": 140
		},
		{
			"label": _("Lifting Date"),
			"fieldname": "lifting_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Purchase Ref"),
			"fieldname": "purchase",
			"fieldtype": "Link",
			"options": "Cement Purchase",
			"width": 130
		},
		{
			"label": _("Factory Plant"),
			"fieldname": "factory",
			"fieldtype": "Link",
			"options": "Cement Factory",
			"width": 140
		},
		{
			"label": _("Project / Customer"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Truck"),
			"fieldname": "truck",
			"fieldtype": "Link",
			"options": "Truck",
			"width": 110
		},
		{
			"label": _("Coupon Ref"),
			"fieldname": "coupon",
			"fieldtype": "Link",
			"options": "Cement Coupon",
			"width": 120
		},
		{
			"label": _("Delivery Note"),
			"fieldname": "delivery_note_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Factory Weight (Tons)"),
			"fieldname": "factory_weight",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Buyer Weight (Tons)"),
			"fieldname": "buyer_weighbridge_qty",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Shortage (Tons)"),
			"fieldname": "shortage_qty",
			"fieldtype": "Float",
			"width": 130
		},
		{
			"label": _("Shortage Penalty"),
			"fieldname": "shortage_penalty",
			"fieldtype": "Currency",
			"width": 140
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		}
	]


def get_data(filters=None):
	if not frappe.db.table_exists("Cement Lifting"):
		return []

	conditions = ["docstatus < 2"]
	values = {}

	if filters:
		if filters.get("customer"):
			conditions.append("customer = %(customer)s")
			values["customer"] = filters.get("customer")
		if filters.get("factory"):
			conditions.append("factory = %(factory)s")
			values["factory"] = filters.get("factory")
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters.get("status")
		if filters.get("from_date"):
			conditions.append("lifting_date >= %(from_date)s")
			values["from_date"] = filters.get("from_date")
		if filters.get("to_date"):
			conditions.append("lifting_date <= %(to_date)s")
			values["to_date"] = filters.get("to_date")

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			name,
			lifting_date,
			purchase,
			factory,
			COALESCE(customer_name, customer) as customer_name,
			truck,
			coupon,
			delivery_note_no,
			factory_weight,
			buyer_weighbridge_qty,
			shortage_qty,
			shortage_penalty,
			status
		FROM `tabCement Lifting`
		WHERE {where_clause}
		ORDER BY lifting_date DESC, creation DESC
	""", values, as_dict=True)


def get_chart_data(data):
	if not data:
		return None

	factory_tons = {}
	for row in data:
		fac = row.get("factory") or _("Direct Plant")
		factory_tons[fac] = factory_tons.get(fac, 0.0) + flt(row.get("buyer_weighbridge_qty", 0))

	sorted_facs = sorted(factory_tons.items(), key=lambda x: x[1], reverse=True)[:6]
	labels = [f[0] for f in sorted_facs]
	values = [round(f[1], 1) for f in sorted_facs]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Buyer Weight (Tons)"), "values": values}]
		},
		"type": "bar",
		"colors": ["#10b981"]
	}


def get_report_summary(data):
	if not data:
		return []

	total_factory_tons = sum(flt(r.get("factory_weight", 0)) for r in data)
	total_buyer_tons = sum(flt(r.get("buyer_weighbridge_qty", 0)) for r in data)
	total_short_tons = sum(flt(r.get("shortage_qty", 0)) for r in data)
	total_penalty = sum(flt(r.get("shortage_penalty", 0)) for r in data)

	return [
		{
			"value": round(total_factory_tons, 1),
			"label": _("Factory Weight (Tons)"),
			"datatype": "Float",
			"indicator": "Blue"
		},
		{
			"value": round(total_buyer_tons, 1),
			"label": _("Delivered Tonnage (Tons)"),
			"datatype": "Float",
			"indicator": "Green"
		},
		{
			"value": round(total_short_tons, 1),
			"label": _("Shortage Variance (Tons)"),
			"datatype": "Float",
			"indicator": "Red"
		},
		{
			"value": round(total_penalty, 2),
			"label": _("Total Penalties (ETB)"),
			"datatype": "Currency",
			"indicator": "Orange"
		}
	]
