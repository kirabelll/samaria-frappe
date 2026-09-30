# -*- coding: utf-8 -*-
"""
Project Financial Summary Report
Cross-division profitability view: contract value vs executed revenue, freight paid, shortages, net margin.
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
		{"label": _("Agreement"),          "fieldname": "name",            "fieldtype": "Link",     "options": "Sales Agreement", "width": 145},
		{"label": _("Project / Site"),      "fieldname": "offloading_site", "fieldtype": "Data",     "width": 160},
		{"label": _("Customer"),            "fieldname": "customer_name",   "fieldtype": "Data",     "width": 180},
		{"label": _("Division"),            "fieldname": "division",        "fieldtype": "Data",     "width": 100},
		{"label": _("Contract Value"),      "fieldname": "total_amount",    "fieldtype": "Currency", "width": 140},
		{"label": _("Executed Revenue"),    "fieldname": "exec_revenue",    "fieldtype": "Currency", "width": 140},
		{"label": _("Freight Paid (ETB)"),  "fieldname": "freight_paid",    "fieldtype": "Currency", "width": 130},
		{"label": _("Shortage Loss"),       "fieldname": "shortage_loss",   "fieldtype": "Currency", "width": 120},
		{"label": _("Net Margin (ETB)"),    "fieldname": "net_margin",      "fieldtype": "Currency", "width": 130},
		{"label": _("Margin %"),            "fieldname": "margin_pct",      "fieldtype": "Percent",  "width": 95},
		{"label": _("Status"),              "fieldname": "status",          "fieldtype": "Data",     "width": 90},
	]


def get_data(filters=None):
	if not frappe.db.table_exists("tabSales Agreement"):
		return []

	conditions = ["1=1"]
	values = {}

	if filters:
		if filters.get("customer"):
			conditions.append("customer = %(customer)s")
			values["customer"] = filters["customer"]
		if filters.get("division"):
			conditions.append("division = %(division)s")
			values["division"] = filters["division"]
		if filters.get("status"):
			conditions.append("status = %(status)s")
			values["status"] = filters["status"]

	where = " AND ".join(conditions)
	agreements = frappe.db.sql(f"""
		SELECT name,
			COALESCE(customer_name, customer) AS customer_name,
			customer, division, offloading_site,
			COALESCE(total_amount, 0) AS total_amount,
			status
		FROM `tabSales Agreement`
		WHERE {where}
		ORDER BY valid_from DESC
	""", values, as_dict=True)

	result = []
	for agr in agreements:
		exec_revenue = 0.0
		freight_paid = 0.0
		shortage_loss = 0.0

		# Pull aggregate actuals for this customer
		if frappe.db.table_exists("tabAggregate Delivery"):
			agg = frappe.db.sql("""
				SELECT
					COALESCE(SUM(customer_receivable), 0) AS revenue,
					COALESCE(SUM(gross_truck_fee), 0)     AS freight,
					COALESCE(SUM(shortage_deduction), 0)  AS shortage
				FROM `tabAggregate Delivery`
				WHERE customer = %(customer)s AND docstatus = 1
			""", {"customer": agr.customer}, as_dict=True)
			if agg:
				exec_revenue  += flt(agg[0].revenue)
				freight_paid  += flt(agg[0].freight)
				shortage_loss += flt(agg[0].shortage)

		# Pull cement actuals for this customer
		if frappe.db.table_exists("tabCement Lifting"):
			cem = frappe.db.sql("""
				SELECT
					COALESCE(SUM(factory_weight), 0)   AS revenue_tons,
					COALESCE(SUM(shortage_penalty), 0) AS shortage
				FROM `tabCement Lifting`
				WHERE customer = %(customer)s AND docstatus = 1
			""", {"customer": agr.customer}, as_dict=True)
			if cem:
				shortage_loss += flt(cem[0].shortage)

		net_margin  = exec_revenue - freight_paid - shortage_loss
		contract    = flt(agr.total_amount)
		margin_pct  = round((net_margin / contract * 100) if contract > 0 else 0.0, 1)

		result.append({
			"name":           agr.name,
			"customer_name":  agr.customer_name,
			"division":       agr.division,
			"offloading_site": agr.offloading_site or "",
			"total_amount":   contract,
			"exec_revenue":   round(exec_revenue, 2),
			"freight_paid":   round(freight_paid, 2),
			"shortage_loss":  round(shortage_loss, 2),
			"net_margin":     round(net_margin, 2),
			"margin_pct":     margin_pct,
			"status":         agr.status,
		})

	return result


def get_chart_data(data):
	if not data:
		return None
	top = sorted(data, key=lambda x: flt(x.get("exec_revenue")), reverse=True)[:6]
	labels   = [r.get("customer_name") or r.get("name") for r in top]
	revenues = [flt(r.get("exec_revenue")) for r in top]
	margins  = [flt(r.get("net_margin")) for r in top]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Executed Revenue (ETB)"), "values": revenues},
				{"name": _("Net Margin (ETB)"),       "values": margins}
			]
		},
		"type": "bar",
		"colors": ["#3b82f6", "#10b981"],
		"barOptions": {"stacked": 0}
	}


def get_report_summary(data):
	if not data:
		return []
	return [
		{"value": round(sum(flt(r.get("total_amount"))  for r in data), 2),
		 "label": _("Total Committed (ETB)"),   "datatype": "Currency", "indicator": "Blue"},
		{"value": round(sum(flt(r.get("exec_revenue"))  for r in data), 2),
		 "label": _("Executed Revenue (ETB)"),   "datatype": "Currency", "indicator": "Green"},
		{"value": round(sum(flt(r.get("freight_paid"))  for r in data), 2),
		 "label": _("Total Freight Paid (ETB)"), "datatype": "Currency", "indicator": "Orange"},
		{"value": round(sum(flt(r.get("net_margin"))    for r in data), 2),
		 "label": _("Estimated Net Margin (ETB)"), "datatype": "Currency", "indicator": "Green"},
	]
