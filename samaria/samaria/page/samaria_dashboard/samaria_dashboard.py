# -*- coding: utf-8 -*-
"""
Samaria Executive Dashboard — Backend Controller
Aggregates real-time KPI metrics across Aggregate, Cement, Medical and Commercial divisions.
Frappe v15
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate, add_days


@frappe.whitelist()
def get_dashboard_data(customer=None, from_date=None, to_date=None):
	"""Return structured metrics, chart data and recent activity for the dashboard."""
	data = {
		"metrics": {
			"aggregate": {
				"total_dispatches":  0,
				"delivered_volume":  0.0,
				"shortage_volume":   0.0,
				"net_profit":        0.0,
				"gross_truck_fee":   0.0,
			},
			"cement": {
				"total_liftings":     0,
				"total_weight_tons":  0.0,
				"total_shortage_tons": 0.0,
				"total_penalties":    0.0,
			},
			"medical": {
				"active_batches":      0,
				"quarantined_batches": 0,
				"near_expiry_batches": 0,
				"pending_requests":    0,
			},
			"commercial": {
				"active_agreements":   0,
				"total_contract_value": 0.0,
			},
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
			},
		},
		"recent_dispatches": [],
		"recent_liftings":   [],
		"urgent_medical":    [],
	}

	# ── 1. Aggregate Deliveries ──────────────────────────────────────────
	if frappe.db.table_exists("tabAggregate Delivery"):
		conds = ["docstatus < 2"]
		vals  = {}
		if customer:
			conds.append("customer = %(customer)s");   vals["customer"]  = customer
		if from_date:
			conds.append("dispatch_date >= %(from_date)s"); vals["from_date"] = from_date
		if to_date:
			conds.append("dispatch_date <= %(to_date)s");   vals["to_date"]   = to_date
		wh = " AND ".join(conds)

		row = frappe.db.sql(f"""
			SELECT COUNT(name) AS cnt,
				   COALESCE(SUM(delivered_volume),  0) AS del_vol,
				   COALESCE(SUM(shortage_volume),   0) AS short_vol,
				   COALESCE(SUM(net_profit_amount),  0) AS profit,
				   COALESCE(SUM(gross_truck_fee),    0) AS truck_fee
			FROM `tabAggregate Delivery` WHERE {wh}
		""", vals, as_dict=True)
		if row:
			r = row[0]
			data["metrics"]["aggregate"]["total_dispatches"] = r.cnt or 0
			data["metrics"]["aggregate"]["delivered_volume"] = round(flt(r.del_vol),  1)
			data["metrics"]["aggregate"]["shortage_volume"]  = round(flt(r.short_vol), 1)
			data["metrics"]["aggregate"]["net_profit"]       = round(flt(r.profit),   2)
			data["metrics"]["aggregate"]["gross_truck_fee"]  = round(flt(r.truck_fee), 2)

		trend = frappe.db.sql(f"""
			SELECT dispatch_date, SUM(delivered_volume) AS vol
			FROM `tabAggregate Delivery` WHERE {wh}
			GROUP BY dispatch_date ORDER BY dispatch_date DESC LIMIT 7
		""", vals, as_dict=True)
		trend.reverse()
		for t in trend:
			data["charts"]["aggregate_trend"]["labels"].append(str(t.dispatch_date))
			data["charts"]["aggregate_trend"]["datasets"][0]["values"].append(round(flt(t.vol), 1))

		data["recent_dispatches"] = frappe.db.sql(f"""
			SELECT name, pad_number, customer_name, item_name,
				   delivered_volume, net_profit_amount, status, dispatch_date
			FROM `tabAggregate Delivery` WHERE {wh}
			ORDER BY dispatch_date DESC, creation DESC LIMIT 5
		""", vals, as_dict=True)

	# ── 2. Cement Liftings ───────────────────────────────────────────────
	if frappe.db.table_exists("tabCement Lifting"):
		cc = ["docstatus < 2"]
		cv = {}
		if customer:
			cc.append("customer = %(customer)s"); cv["customer"]  = customer
		if from_date:
			cc.append("lifting_date >= %(from_date)s"); cv["from_date"] = from_date
		if to_date:
			cc.append("lifting_date <= %(to_date)s");   cv["to_date"]   = to_date
		cw = " AND ".join(cc)

		crow = frappe.db.sql(f"""
			SELECT COUNT(name) AS cnt,
				   COALESCE(SUM(buyer_weighbridge_qty), 0) AS wt,
				   COALESCE(SUM(shortage_qty), 0)          AS short,
				   COALESCE(SUM(shortage_penalty), 0)       AS pen
			FROM `tabCement Lifting` WHERE {cw}
		""", cv, as_dict=True)
		if crow:
			cr = crow[0]
			data["metrics"]["cement"]["total_liftings"]      = cr.cnt or 0
			data["metrics"]["cement"]["total_weight_tons"]   = round(flt(cr.wt),    1)
			data["metrics"]["cement"]["total_shortage_tons"] = round(flt(cr.short),  1)
			data["metrics"]["cement"]["total_penalties"]     = round(flt(cr.pen),    2)

		frows = frappe.db.sql(f"""
			SELECT factory, SUM(buyer_weighbridge_qty) AS tons
			FROM `tabCement Lifting`
			WHERE {cw} AND factory IS NOT NULL AND factory != ''
			GROUP BY factory ORDER BY tons DESC LIMIT 5
		""", cv, as_dict=True)
		for fr in frows:
			data["charts"]["cement_by_factory"]["labels"].append(fr.factory)
			data["charts"]["cement_by_factory"]["datasets"][0]["values"].append(round(flt(fr.tons), 1))

		data["recent_liftings"] = frappe.db.sql(f"""
			SELECT name, factory, customer_name,
				   buyer_weighbridge_qty, shortage_qty, status, lifting_date
			FROM `tabCement Lifting` WHERE {cw}
			ORDER BY lifting_date DESC, creation DESC LIMIT 5
		""", cv, as_dict=True)

	# ── 3. Medical ────────────────────────────────────────────────────────
	if frappe.db.table_exists("tabMedical Batch"):
		data["metrics"]["medical"]["active_batches"]      = frappe.db.count("Medical Batch", {"status": "Available"})
		data["metrics"]["medical"]["quarantined_batches"] = frappe.db.count("Medical Batch", {"status": "Quarantine"})
		ninety = add_days(nowdate(), 90)
		data["metrics"]["medical"]["near_expiry_batches"] = frappe.db.count(
			"Medical Batch", {"status": "Available", "expiry_date": ["between", [nowdate(), ninety]]}
		)

	if frappe.db.table_exists("tabMedical Request"):
		data["metrics"]["medical"]["pending_requests"] = frappe.db.count(
			"Medical Request", {"status": ["in", ["Submitted", "Quoted", "Approved"]]}
		)
		data["urgent_medical"] = frappe.get_all(
			"Medical Request",
			filters={"status": ["in", ["Submitted", "Quoted", "Approved"]]},
			fields=["name", "customer_name", "priority", "status", "request_date"],
			order_by="creation desc",
			limit=5
		)

	# ── 4. Commercial Agreements ──────────────────────────────────────────
	if frappe.db.table_exists("tabSales Agreement"):
		data["metrics"]["commercial"]["active_agreements"] = frappe.db.count("Sales Agreement", {"status": "Active"})
		val = frappe.db.sql("""
			SELECT COALESCE(SUM(total_amount), 0) AS total_val
			FROM `tabSales Agreement` WHERE status = 'Active'
		""", as_dict=True)
		if val:
			data["metrics"]["commercial"]["total_contract_value"] = round(flt(val[0].total_val), 2)

	# ── 5. Division mix pie ───────────────────────────────────────────────
	data["charts"]["division_mix"]["datasets"][0]["values"] = [
		data["metrics"]["aggregate"]["total_dispatches"],
		data["metrics"]["cement"]["total_liftings"],
		data["metrics"]["medical"]["active_batches"],
		data["metrics"]["commercial"]["active_agreements"],
	]

	return data


@frappe.whitelist()
def get_project_filters():
	"""Return Customer list for filter dropdowns."""
	return frappe.get_all("Customer", fields=["name", "customer_name"], order_by="customer_name asc")
