# -*- coding: utf-8 -*-
"""
Cement Project Lifting and Balance Report
Tracks cement liftings with factory/buyer weighbridge data, shortage analysis, coupon usage and purchase balance.
Frappe v15
"""
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data    = get_data(filters)
	chart   = get_chart_data(data)
	summary = get_report_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Lifting ID"),          "fieldname": "name",                    "fieldtype": "Link",     "options": "Cement Lifting", "width": 145},
		{"label": _("Date"),                 "fieldname": "lifting_date",            "fieldtype": "Date",     "width": 100},
		{"label": _("Purchase Ref"),         "fieldname": "purchase",                "fieldtype": "Link",     "options": "Cement Purchase", "width": 120},
		{"label": _("Factory"),              "fieldname": "factory",                 "fieldtype": "Link",     "options": "Cement Factory",  "width": 140},
		{"label": _("Customer"),             "fieldname": "customer_name",           "fieldtype": "Data",     "width": 180},
		{"label": _("Truck"),                "fieldname": "truck",                   "fieldtype": "Link",     "options": "Truck",           "width": 100},
		{"label": _("Coupon"),               "fieldname": "coupon",                  "fieldtype": "Link",     "options": "Cement Coupon",   "width": 120},
		{"label": _("Delivery Note"),        "fieldname": "delivery_note_no",        "fieldtype": "Data",     "width": 120},
		{"label": _("Factory WB Ref"),       "fieldname": "factory_weighbridge_ref", "fieldtype": "Data",     "width": 120},
		{"label": _("Factory Wt (Tons)"),    "fieldname": "factory_weight",          "fieldtype": "Float",    "width": 115},
		{"label": _("Buyer Wt (Tons)"),      "fieldname": "buyer_weighbridge_qty",   "fieldtype": "Float",    "width": 115},
		{"label": _("Shortage (Tons)"),      "fieldname": "shortage_qty",            "fieldtype": "Float",    "width": 115},
		{"label": _("Shortage Penalty"),     "fieldname": "shortage_penalty",        "fieldtype": "Currency", "width": 130},
		{"label": _("Status"),               "fieldname": "status",                  "fieldtype": "Data",     "width": 90},
	]


def get_data(filters=None):
	if not frappe.db.table_exists("tabCement Lifting"):
		return []

	conditions = ["docstatus < 2"]
	values = {}

	if filters:
		if filters.get("customer"):
			conditions.append("customer = %(customer)s")
			values["customer"] = filters["customer"]
		if filters.get("factory"):
			conditions.append("factory = %(factory)s")
			values["factory"] = filters["factory"]
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters["status"]
		if filters.get("from_date"):
			conditions.append("lifting_date >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("lifting_date <= %(to_date)s")
			values["to_date"] = filters["to_date"]

	where = " AND ".join(conditions)
	rows = frappe.db.sql(f"""
		SELECT
			name, lifting_date, purchase, factory,
			COALESCE(customer_name, customer) AS customer_name,
			truck, coupon, delivery_note_no,
			factory_weighbridge_ref,
			COALESCE(factory_weight, 0)        AS factory_weight,
			COALESCE(buyer_weighbridge_qty, 0)  AS buyer_weighbridge_qty,
			COALESCE(shortage_qty, 0)           AS shortage_qty,
			COALESCE(shortage_penalty, 0)       AS shortage_penalty,
			status
		FROM `tabCement Lifting`
		WHERE {where}
		ORDER BY lifting_date DESC, creation DESC
	""", values, as_dict=True)
	return rows


def get_chart_data(data):
	if not data:
		return None
	factory_tons = {}
	for row in data:
		fac = row.get("factory") or _("Unknown")
		factory_tons[fac] = factory_tons.get(fac, 0.0) + flt(row.get("buyer_weighbridge_qty"))

	top = sorted(factory_tons.items(), key=lambda x: x[1], reverse=True)[:6]
	return {
		"data": {
			"labels": [f[0] for f in top],
			"datasets": [{"name": _("Delivered Tons"), "values": [round(f[1], 1) for f in top]}]
		},
		"type": "bar",
		"colors": ["#10b981"]
	}


def get_report_summary(data):
	if not data:
		return []
	factory_wt  = sum(flt(r.get("factory_weight")) for r in data)
	buyer_wt    = sum(flt(r.get("buyer_weighbridge_qty")) for r in data)
	shortage    = sum(flt(r.get("shortage_qty")) for r in data)
	penalties   = sum(flt(r.get("shortage_penalty")) for r in data)
	return [
		{"value": round(factory_wt, 1),  "label": _("Factory Weight (Tons)"),  "datatype": "Float",    "indicator": "Blue"},
		{"value": round(buyer_wt, 1),    "label": _("Delivered Tons (Buyer)"),  "datatype": "Float",    "indicator": "Green"},
		{"value": round(shortage, 1),    "label": _("Total Shortage (Tons)"),   "datatype": "Float",    "indicator": "Orange"},
		{"value": round(penalties, 2),   "label": _("Total Penalties (ETB)"),   "datatype": "Currency", "indicator": "Red"},
	]
