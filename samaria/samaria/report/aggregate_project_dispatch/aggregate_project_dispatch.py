# -*- coding: utf-8 -*-
"""
Aggregate Project Dispatch Report
Tracks stone & aggregate dispatches, weighbridge variances, transport settlements, and margins by client project.
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
			"label": _("Dispatch ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Aggregate Delivery",
			"width": 140
		},
		{
			"label": _("Dispatch Date"),
			"fieldname": "dispatch_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Project / Customer"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Quarry / Supplier"),
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": _("Transporter"),
			"fieldname": "transporter_name",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": _("Truck"),
			"fieldname": "truck",
			"fieldtype": "Link",
			"options": "Truck",
			"width": 100
		},
		{
			"label": _("Pad / Receipt"),
			"fieldname": "pad_number",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Material"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Loaded (m³)"),
			"fieldname": "loaded_volume",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Delivered (m³)"),
			"fieldname": "delivered_volume",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Shortage (m³)"),
			"fieldname": "shortage_volume",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Rate (ETB)"),
			"fieldname": "transport_rate",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Gross Truck Fee"),
			"fieldname": "gross_truck_fee",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Shortage Deduction"),
			"fieldname": "shortage_deduction",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Net Truck Payment"),
			"fieldname": "net_truck_payment",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Customer Receivable"),
			"fieldname": "customer_receivable",
			"fieldtype": "Currency",
			"width": 140
		},
		{
			"label": _("Net Profit Amount"),
			"fieldname": "net_profit_amount",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		}
	]


def get_data(filters=None):
	if not frappe.db.table_exists("Aggregate Delivery"):
		return []

	conditions = ["docstatus < 2"]
	values = {}

	if filters:
		if filters.get("customer"):
			conditions.append("customer = %(customer)s")
			values["customer"] = filters.get("customer")
		if filters.get("supplier"):
			conditions.append("supplier = %(supplier)s")
			values["supplier"] = filters.get("supplier")
		if filters.get("transporter"):
			conditions.append("transporter = %(transporter)s")
			values["transporter"] = filters.get("transporter")
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters.get("status")
		if filters.get("from_date"):
			conditions.append("dispatch_date >= %(from_date)s")
			values["from_date"] = filters.get("from_date")
		if filters.get("to_date"):
			conditions.append("dispatch_date <= %(to_date)s")
			values["to_date"] = filters.get("to_date")

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			name,
			dispatch_date,
			COALESCE(customer_name, customer) as customer_name,
			COALESCE(supplier_name, supplier) as supplier_name,
			COALESCE(transporter_name, transporter) as transporter_name,
			truck,
			pad_number,
			COALESCE(item_name, item_code) as item_name,
			loaded_volume,
			delivered_volume,
			shortage_volume,
			transport_rate,
			gross_truck_fee,
			shortage_deduction,
			net_truck_payment,
			customer_receivable,
			net_profit_amount,
			status
		FROM `tabAggregate Delivery`
		WHERE {where_clause}
		ORDER BY dispatch_date DESC, creation DESC
	""", values, as_dict=True)


def get_chart_data(data):
	if not data:
		return None

	project_vols = {}
	for row in data:
		proj = row.get("customer_name") or _("Unassigned")
		project_vols[proj] = project_vols.get(proj, 0.0) + flt(row.get("delivered_volume", 0))

	# Top 6 projects
	sorted_projects = sorted(project_vols.items(), key=lambda x: x[1], reverse=True)[:6]
	labels = [p[0] for p in sorted_projects]
	values = [round(p[1], 1) for p in sorted_projects]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Delivered Volume (m³)"), "values": values}]
		},
		"type": "bar",
		"colors": ["#f97316"]
	}


def get_report_summary(data):
	if not data:
		return []

	total_del_vol = sum(flt(r.get("delivered_volume", 0)) for r in data)
	total_short_vol = sum(flt(r.get("shortage_volume", 0)) for r in data)
	total_profit = sum(flt(r.get("net_profit_amount", 0)) for r in data)
	total_short_deduct = sum(flt(r.get("shortage_deduction", 0)) for r in data)

	return [
		{
			"value": round(total_del_vol, 1),
			"label": _("Delivered Volume (m³)"),
			"datatype": "Float",
			"indicator": "Blue"
		},
		{
			"value": round(total_short_vol, 1),
			"label": _("Shortage Volume (m³)"),
			"datatype": "Float",
			"indicator": "Red"
		},
		{
			"value": round(total_short_deduct, 2),
			"label": _("Shortage Deductions (ETB)"),
			"datatype": "Currency",
			"indicator": "Orange"
		},
		{
			"value": round(total_profit, 2),
			"label": _("Total Net Profit (ETB)"),
			"datatype": "Currency",
			"indicator": "Green"
		}
	]
