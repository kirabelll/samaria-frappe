# -*- coding: utf-8 -*-
"""
Project Financial Summary Report
Cross-division executive profitability and operational commitment analysis by project.
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
			"label": _("Agreement Ref"),
			"fieldname": "agreement",
			"fieldtype": "Link",
			"options": "Sales Agreement",
			"width": 140
		},
		{
			"label": _("Project / Offloading Site"),
			"fieldname": "project_site",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Customer Entity"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Division"),
			"fieldname": "division",
			"fieldtype": "Data",
			"width": 110
		},
		{
			"label": _("Contract Value (ETB)"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Executed Revenue (ETB)"),
			"fieldname": "executed_revenue",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": _("Freight & Haulage Paid"),
			"fieldname": "freight_paid",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Shortage Penalties"),
			"fieldname": "shortages_deducted",
			"fieldtype": "Currency",
			"width": 140
		},
		{
			"label": _("Estimated Net Margin"),
			"fieldname": "net_margin",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Margin %"),
			"fieldname": "margin_pct",
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"label": _("Agreement Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		}
	]


def get_data(filters=None):
	if not frappe.db.table_exists("Sales Agreement"):
		return []

	conds = ["docstatus < 2"]
	vals = {}

	if filters:
		if filters.get("customer"):
			conds.append("customer = %(customer)s")
			vals["customer"] = filters.get("customer")
		if filters.get("division"):
			conds.append("division = %(division)s")
			vals["division"] = filters.get("division")
		if filters.get("status"):
			conds.append("status = %(status)s")
			vals["status"] = filters.get("status")

	where_clause = " AND ".join(conds)

	agreements = frappe.db.sql(f"""
		SELECT
			name as agreement,
			customer,
			COALESCE(customer_name, customer) as customer_name,
			division,
			offloading_site as project_site,
			total_amount,
			status
		FROM `tabSales Agreement`
		WHERE {where_clause}
		ORDER BY total_amount DESC, creation DESC
	""", vals, as_dict=True)

	rows = []
	for agr in agreements:
		cust = agr.customer
		div = agr.division or "Aggregate"
		contract_val = flt(agr.total_amount)

		executed_rev = 0.0
		freight_paid = 0.0
		shortages = 0.0
		net_margin = 0.0

		# Aggregate calculation
		if div in ("Aggregate", "General") and frappe.db.table_exists("Aggregate Delivery"):
			agg_res = frappe.db.sql("""
				SELECT
					COALESCE(SUM(customer_receivable), 0) as rev,
					COALESCE(SUM(net_truck_payment), 0) as freight,
					COALESCE(SUM(shortage_deduction), 0) as short,
					COALESCE(SUM(net_profit_amount), 0) as profit
				FROM `tabAggregate Delivery`
				WHERE customer = %s AND docstatus < 2
			""", (cust,), as_dict=True)

			if agg_res:
				ar = agg_res[0]
				executed_rev += flt(ar.rev)
				freight_paid += flt(ar.freight)
				shortages += flt(ar.short)
				net_margin += flt(ar.profit)

		# Cement calculation
		if div in ("Cement", "General") and frappe.db.table_exists("Cement Lifting"):
			cem_res = frappe.db.sql("""
				SELECT
					COALESCE(SUM(shortage_penalty), 0) as penalty,
					COALESCE(SUM(buyer_weighbridge_qty), 0) as qty
				FROM `tabCement Lifting`
				WHERE customer = %s AND docstatus < 2
			""", (cust,), as_dict=True)

			if cem_res:
				cr = cem_res[0]
				shortages += flt(cr.penalty)
				# If aggregate profit wasn't primary, estimate cement margin
				if net_margin == 0 and flt(cr.qty) > 0:
					executed_rev += flt(cr.qty) * 8000.0  # approximate standard tonnage valuation
					net_margin += (executed_rev * 0.08) - flt(cr.penalty)

		margin_pct = (net_margin / executed_rev * 100.0) if executed_rev > 0 else 0.0

		rows.append({
			"agreement": agr.agreement,
			"project_site": agr.project_site or agr.customer_name,
			"customer_name": agr.customer_name,
			"division": div,
			"total_amount": contract_val,
			"executed_revenue": round(executed_rev, 2),
			"freight_paid": round(freight_paid, 2),
			"shortages_deducted": round(shortages, 2),
			"net_margin": round(net_margin, 2),
			"margin_pct": round(margin_pct, 1),
			"status": agr.status
		})

	return rows


def get_chart_data(data):
	if not data:
		return None

	labels = []
	margin_values = []
	rev_values = []

	for row in data[:6]:
		proj = row.get("project_site") or row.get("agreement")
		labels.append(proj[:18])
		margin_values.append(flt(row.get("net_margin", 0)))
		rev_values.append(flt(row.get("executed_revenue", 0)))

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Executed Revenue (ETB)"), "values": rev_values},
				{"name": _("Net Margin (ETB)"), "values": margin_values}
			]
		},
		"type": "bar",
		"colors": ["#3b82f6", "#10b981"]
	}


def get_report_summary(data):
	if not data:
		return []

	total_contract = sum(flt(r.get("total_amount", 0)) for r in data)
	total_executed = sum(flt(r.get("executed_revenue", 0)) for r in data)
	total_freight = sum(flt(r.get("freight_paid", 0)) for r in data)
	total_margin = sum(flt(r.get("net_margin", 0)) for r in data)

	return [
		{
			"value": round(total_contract, 2),
			"label": _("Total Committed Value (ETB)"),
			"datatype": "Currency",
			"indicator": "Purple"
		},
		{
			"value": round(total_executed, 2),
			"label": _("Executed Turnover (ETB)"),
			"datatype": "Currency",
			"indicator": "Blue"
		},
		{
			"value": round(total_freight, 2),
			"label": _("Freight / Logistics Paid (ETB)"),
			"datatype": "Currency",
			"indicator": "Orange"
		},
		{
			"value": round(total_margin, 2),
			"label": _("Estimated Net Margin (ETB)"),
			"datatype": "Currency",
			"indicator": "Green"
		}
	]
