# -*- coding: utf-8 -*-
"""
Samaria Executive Dashboard Backend Controller
Frappe Framework Version-16
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate, add_days


@frappe.whitelist()
def get_dashboard_data(customer=None, from_date=None, to_date=None):
	"""
	Aggregates multi-division metrics across Aggregate, Cement, Medical, and Commercial agreements.
	"""
	data = {
		"metrics": {
			"aggregate": {
				"total_dispatches": 0,
				"delivered_volume": 0.0,
				"shortage_volume": 0.0,
				"net_profit": 0.0,
				"gross_truck_fee": 0.0
			},
			"cement": {
				"total_liftings": 0,
				"total_weight_tons": 0.0,
				"total_shortage_tons": 0.0,
				"total_penalties": 0.0
			},
			"medical": {
				"active_batches": 0,
				"quarantined_batches": 0,
				"near_expiry_batches": 0,
				"pending_requests": 0
			},
			"commercial": {
				"active_agreements": 0,
				"total_contract_value": 0.0
			}
		},
		"charts": {
			"aggregate_trend": {
				"labels": [],
				"datasets": [{"name": _("Delivered Volume (m³)"), "values": []}]
			},
			"cement_by_factory": {
				"labels": [],
				"datasets": [{"values": []}]
			},
			"division_mix": {
				"labels": [_("Aggregate"), _("Cement"), _("Medical"), _("Commercial")],
				"datasets": [{"values": [0, 0, 0, 0]}]
			}
		},
		"recent_dispatches": [],
		"recent_liftings": [],
		"urgent_medical": []
	}

	# 1. Aggregate Deliveries
	if frappe.db.table_exists("Aggregate Delivery"):
		conds = ["docstatus < 2"]
		vals = {}
		if customer:
			conds.append("customer = %(customer)s")
			vals["customer"] = customer
		if from_date:
			conds.append("dispatch_date >= %(from_date)s")
			vals["from_date"] = from_date
		if to_date:
			conds.append("dispatch_date <= %(to_date)s")
			vals["to_date"] = to_date

		where_clause = " AND ".join(conds)

		agg_summary = frappe.db.sql(f"""
			SELECT
				COUNT(name) as total_count,
				COALESCE(SUM(delivered_volume), 0) as del_vol,
				COALESCE(SUM(shortage_volume), 0) as short_vol,
				COALESCE(SUM(net_profit_amount), 0) as profit,
				COALESCE(SUM(gross_truck_fee), 0) as truck_fee
			FROM `tabAggregate Delivery`
			WHERE {where_clause}
		""", vals, as_dict=True)

		if agg_summary:
			row = agg_summary[0]
			data["metrics"]["aggregate"]["total_dispatches"] = row.total_count or 0
			data["metrics"]["aggregate"]["delivered_volume"] = round(flt(row.del_vol), 1)
			data["metrics"]["aggregate"]["shortage_volume"] = round(flt(row.short_vol), 1)
			data["metrics"]["aggregate"]["net_profit"] = round(flt(row.profit), 2)
			data["metrics"]["aggregate"]["gross_truck_fee"] = round(flt(row.truck_fee), 2)

		# Aggregate Monthly/Daily Trend
		trend_rows = frappe.db.sql(f"""
			SELECT dispatch_date, SUM(delivered_volume) as vol
			FROM `tabAggregate Delivery`
			WHERE {where_clause}
			GROUP BY dispatch_date
			ORDER BY dispatch_date DESC
			LIMIT 7
		""", vals, as_dict=True)

		trend_rows.reverse()
		for r in trend_rows:
			data["charts"]["aggregate_trend"]["labels"].append(str(r.dispatch_date))
			data["charts"]["aggregate_trend"]["datasets"][0]["values"].append(round(flt(r.vol), 1))

		# Recent 5 dispatches
		data["recent_dispatches"] = frappe.db.sql(f"""
			SELECT name, pad_number, customer_name, item_name, delivered_volume, net_profit_amount, status, dispatch_date
			FROM `tabAggregate Delivery`
			WHERE {where_clause}
			ORDER BY dispatch_date DESC, creation DESC
			LIMIT 5
		""", vals, as_dict=True)

	# 2. Cement Lifting
	if frappe.db.table_exists("Cement Lifting"):
		c_conds = ["docstatus < 2"]
		c_vals = {}
		if customer:
			c_conds.append("customer = %(customer)s")
			c_vals["customer"] = customer
		if from_date:
			c_conds.append("lifting_date >= %(from_date)s")
			c_vals["from_date"] = from_date
		if to_date:
			c_conds.append("lifting_date <= %(to_date)s")
			c_vals["to_date"] = to_date

		c_where = " AND ".join(c_conds)

		cement_summary = frappe.db.sql(f"""
			SELECT
				COUNT(name) as total_count,
				COALESCE(SUM(buyer_weighbridge_qty), 0) as total_tons,
				COALESCE(SUM(shortage_qty), 0) as short_tons,
				COALESCE(SUM(shortage_penalty), 0) as penalties
			FROM `tabCement Lifting`
			WHERE {c_where}
		""", c_vals, as_dict=True)

		if cement_summary:
			c_row = cement_summary[0]
			data["metrics"]["cement"]["total_liftings"] = c_row.total_count or 0
			data["metrics"]["cement"]["total_weight_tons"] = round(flt(c_row.total_tons), 1)
			data["metrics"]["cement"]["total_shortage_tons"] = round(flt(c_row.short_tons), 1)
			data["metrics"]["cement"]["total_penalties"] = round(flt(c_row.penalties), 2)

		# Cement by Factory chart
		factory_rows = frappe.db.sql(f"""
			SELECT factory, SUM(buyer_weighbridge_qty) as total_tons
			FROM `tabCement Lifting`
			WHERE {c_where} AND factory IS NOT NULL AND factory != ''
			GROUP BY factory
			ORDER BY total_tons DESC
			LIMIT 5
		""", c_vals, as_dict=True)

		for fr in factory_rows:
			data["charts"]["cement_by_factory"]["labels"].append(fr.factory)
			data["charts"]["cement_by_factory"]["datasets"][0]["values"].append(round(flt(fr.total_tons), 1))

		# Recent 5 liftings
		data["recent_liftings"] = frappe.db.sql(f"""
			SELECT name, factory, customer_name, buyer_weighbridge_qty, shortage_qty, status, lifting_date
			FROM `tabCement Lifting`
			WHERE {c_where}
			ORDER BY lifting_date DESC, creation DESC
			LIMIT 5
		""", c_vals, as_dict=True)

	# 3. Medical Batches & Requests
	if frappe.db.table_exists("Medical Batch"):
		data["metrics"]["medical"]["active_batches"] = frappe.db.count("Medical Batch", {"is_quarantined": 0})
		data["metrics"]["medical"]["quarantined_batches"] = frappe.db.count("Medical Batch", {"is_quarantined": 1})

		ninety_days = add_days(nowdate(), 90)
		data["metrics"]["medical"]["near_expiry_batches"] = frappe.db.count(
			"Medical Batch",
			{"expiry_date": ["between", [nowdate(), ninety_days]]}
		)

	if frappe.db.table_exists("Medical Request"):
		data["metrics"]["medical"]["pending_requests"] = frappe.db.count(
			"Medical Request",
			{"status": ["in", ["Submitted", "Quoted", "Approved"]]}
		)
		data["urgent_medical"] = frappe.get_all(
			"Medical Request",
			filters={"status": ["in", ["Submitted", "Quoted", "Approved"]]},
			fields=["name", "customer_name", "priority", "status", "request_date"],
			order_by="creation desc",
			limit=5
		)

	# 4. Sales Agreements
	if frappe.db.table_exists("Sales Agreement"):
		data["metrics"]["commercial"]["active_agreements"] = frappe.db.count("Sales Agreement", {"status": "Active"})
		agr_val = frappe.db.sql("""
			SELECT COALESCE(SUM(total_amount), 0) as total_val
			FROM `tabSales Agreement`
			WHERE status = 'Active'
		""", as_dict=True)
		if agr_val:
			data["metrics"]["commercial"]["total_contract_value"] = round(flt(agr_val[0].total_val), 2)

	# Division mix chart
	data["charts"]["division_mix"]["datasets"][0]["values"] = [
		data["metrics"]["aggregate"]["total_dispatches"],
		data["metrics"]["cement"]["total_liftings"],
		data["metrics"]["medical"]["active_batches"],
		data["metrics"]["commercial"]["active_agreements"]
	]

	return data


@frappe.whitelist()
def get_project_filters():
	"""Fetches list of customers and offloading sites for dashboard filter dropdown."""
	customers = []
	try:
		if frappe.db.table_exists("Customer"):
			customers = frappe.get_all("Customer", fields=["name", "customer_name"], order_by="customer_name asc", limit=50)
	except Exception:
		pass
	return customers
