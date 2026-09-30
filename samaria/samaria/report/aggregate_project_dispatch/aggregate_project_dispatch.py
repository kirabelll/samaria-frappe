# -*- coding: utf-8 -*-
"""
Aggregate Project Dispatch Report
Tracks stone/aggregate dispatches, weighbridge variances, transport costs, and net margins by client project.
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
		{"label": _("Dispatch ID"),         "fieldname": "name",               "fieldtype": "Link",     "options": "Aggregate Delivery", "width": 145},
		{"label": _("Date"),                 "fieldname": "dispatch_date",       "fieldtype": "Date",     "width": 100},
		{"label": _("Customer / Project"),   "fieldname": "customer_name",       "fieldtype": "Data",     "width": 180},
		{"label": _("Supplier / Quarry"),    "fieldname": "supplier_name",       "fieldtype": "Data",     "width": 160},
		{"label": _("Transporter"),          "fieldname": "transporter_name",    "fieldtype": "Data",     "width": 160},
		{"label": _("Truck"),                "fieldname": "truck",               "fieldtype": "Link",     "options": "Truck", "width": 100},
		{"label": _("Pad No"),               "fieldname": "pad_number",          "fieldtype": "Data",     "width": 110},
		{"label": _("Material"),             "fieldname": "item_name",           "fieldtype": "Data",     "width": 130},
		{"label": _("Loaded (m³)"),          "fieldname": "loaded_volume",       "fieldtype": "Float",    "width": 110},
		{"label": _("Delivered (m³)"),       "fieldname": "delivered_volume",    "fieldtype": "Float",    "width": 110},
		{"label": _("Shortage (m³)"),        "fieldname": "shortage_volume",     "fieldtype": "Float",    "width": 110},
		{"label": _("Rate (ETB/m³)"),        "fieldname": "transport_rate",      "fieldtype": "Currency", "width": 110},
		{"label": _("Gross Truck Fee"),      "fieldname": "gross_truck_fee",     "fieldtype": "Currency", "width": 130},
		{"label": _("Shortage Deduction"),   "fieldname": "shortage_deduction",  "fieldtype": "Currency", "width": 135},
		{"label": _("Net Transport (ETB)"),  "fieldname": "net_truck_payment",   "fieldtype": "Currency", "width": 140},
		{"label": _("Customer Receivable"),  "fieldname": "customer_receivable", "fieldtype": "Currency", "width": 140},
		{"label": _("Net Profit (ETB)"),     "fieldname": "net_profit_amount",   "fieldtype": "Currency", "width": 130},
		{"label": _("Status"),               "fieldname": "status",              "fieldtype": "Data",     "width": 90},
	]


def get_data(filters=None):
	if not frappe.db.table_exists("tabAggregate Delivery"):
		return []

	conditions = ["docstatus < 2"]
	values = {}

	if filters:
		if filters.get("customer"):
			conditions.append("customer = %(customer)s")
			values["customer"] = filters["customer"]
		if filters.get("supplier"):
			conditions.append("supplier = %(supplier)s")
			values["supplier"] = filters["supplier"]
		if filters.get("transporter"):
			conditions.append("transporter = %(transporter)s")
			values["transporter"] = filters["transporter"]
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters["status"]
		if filters.get("from_date"):
			conditions.append("dispatch_date >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("dispatch_date <= %(to_date)s")
			values["to_date"] = filters["to_date"]

	where = " AND ".join(conditions)
	return frappe.db.sql(f"""
		SELECT
			name, dispatch_date,
			COALESCE(customer_name, customer) AS customer_name,
			COALESCE(supplier_name, supplier) AS supplier_name,
			COALESCE(transporter_name, transporter) AS transporter_name,
			truck, pad_number,
			COALESCE(item_name, item) AS item_name,
			COALESCE(loaded_volume, 0) AS loaded_volume,
			COALESCE(delivered_volume, 0) AS delivered_volume,
			COALESCE(shortage_volume, 0) AS shortage_volume,
			COALESCE(transport_rate, 0) AS transport_rate,
			COALESCE(gross_truck_fee, 0) AS gross_truck_fee,
			COALESCE(shortage_deduction, 0) AS shortage_deduction,
			COALESCE(net_truck_payment, 0) AS net_truck_payment,
			COALESCE(customer_receivable, 0) AS customer_receivable,
			COALESCE(net_profit_amount, 0) AS net_profit_amount,
			status
		FROM `tabAggregate Delivery`
		WHERE {where}
		ORDER BY dispatch_date DESC, creation DESC
	""", values, as_dict=True)


def get_chart_data(data):
	if not data:
		return None
	proj_vols = {}
	for row in data:
		proj = row.get("customer_name") or _("Unknown")
		proj_vols[proj] = proj_vols.get(proj, 0.0) + flt(row.get("delivered_volume"))

	top = sorted(proj_vols.items(), key=lambda x: x[1], reverse=True)[:6]
	return {
		"data": {
			"labels": [p[0] for p in top],
			"datasets": [{"name": _("Delivered Volume (m³)"), "values": [round(p[1], 1) for p in top]}]
		},
		"type": "bar",
		"colors": ["#f97316"],
		"barOptions": {"stacked": 0}
	}


def get_report_summary(data):
	if not data:
		return []
	return [
		{"value": round(sum(flt(r.get("delivered_volume")) for r in data), 1),
		 "label": _("Delivered Volume (m³)"), "datatype": "Float", "indicator": "Blue"},
		{"value": round(sum(flt(r.get("shortage_volume")) for r in data), 1),
		 "label": _("Shortage Volume (m³)"), "datatype": "Float", "indicator": "Red"},
		{"value": round(sum(flt(r.get("shortage_deduction")) for r in data), 2),
		 "label": _("Shortage Deductions (ETB)"), "datatype": "Currency", "indicator": "Orange"},
		{"value": round(sum(flt(r.get("net_profit_amount")) for r in data), 2),
		 "label": _("Total Net Profit (ETB)"), "datatype": "Currency", "indicator": "Green"},
	]
