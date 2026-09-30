# -*- coding: utf-8 -*-
"""
Samaria Cement API
Exposes cement purchase balance, lifting, and analytics endpoints.
Frappe v15
"""
import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_factory_balances(factory=None):
	"""Return purchased vs remaining balance per factory from active Cement Purchases."""
	if not frappe.db.table_exists("tabCement Purchase"):
		return []

	cond  = "status NOT IN ('Cancelled') AND docstatus < 2"
	vals  = {}
	if factory:
		cond += " AND factory = %(factory)s"
		vals["factory"] = factory

	return frappe.db.sql(f"""
		SELECT
			factory,
			COALESCE(SUM(quantity_tons),    0) AS total_purchased_tons,
			COALESCE(SUM(balance_remaining),0) AS total_remaining_tons,
			COALESCE(SUM(quantity_tons) - SUM(balance_remaining), 0) AS total_lifted_tons,
			COALESCE(SUM(total_amount),     0) AS total_etb_spent,
			COALESCE(SUM(paid_amount),      0) AS total_paid,
			COUNT(name)                         AS purchase_count
		FROM `tabCement Purchase`
		WHERE {cond}
		GROUP BY factory
		ORDER BY total_purchased_tons DESC
	""", vals, as_dict=True)


@frappe.whitelist()
def get_cement_analytics(customer=None, factory=None, from_date=None, to_date=None):
	"""Return overall cement KPI metrics."""
	analytics = {
		"purchases": {
			"purchased_tons": 0.0, "remaining_tons": 0.0,
			"total_etb": 0.0, "active_count": 0
		},
		"liftings": {
			"total_liftings": 0, "lifted_tons": 0.0,
			"shortage_tons": 0.0, "total_penalties": 0.0
		},
		"coupons": {"active_count": 0, "used_count": 0}
	}

	if frappe.db.table_exists("tabCement Purchase"):
		p = frappe.db.sql("""
			SELECT
				COALESCE(SUM(quantity_tons),    0) AS pur_tons,
				COALESCE(SUM(balance_remaining),0) AS rem_tons,
				COALESCE(SUM(total_amount),     0) AS total_etb,
				COUNT(CASE WHEN status = 'Active' THEN 1 END) AS active_cnt
			FROM `tabCement Purchase` WHERE docstatus < 2
		""", as_dict=True)
		if p:
			analytics["purchases"]["purchased_tons"]  = round(flt(p[0].pur_tons),    1)
			analytics["purchases"]["remaining_tons"]  = round(flt(p[0].rem_tons),    1)
			analytics["purchases"]["total_etb"]       = round(flt(p[0].total_etb),   2)
			analytics["purchases"]["active_count"]    = p[0].active_cnt or 0

	if frappe.db.table_exists("tabCement Lifting"):
		conds = ["docstatus < 2"]
		vals  = {}
		if customer:
			conds.append("customer = %(customer)s"); vals["customer"] = customer
		if factory:
			conds.append("factory = %(factory)s");   vals["factory"]  = factory
		if from_date:
			conds.append("lifting_date >= %(from_date)s"); vals["from_date"] = from_date
		if to_date:
			conds.append("lifting_date <= %(to_date)s");   vals["to_date"]   = to_date

		l = frappe.db.sql(f"""
			SELECT
				COUNT(name)                              AS cnt,
				COALESCE(SUM(factory_weight),       0)  AS fac_tons,
				COALESCE(SUM(shortage_qty),         0)  AS short_tons,
				COALESCE(SUM(shortage_penalty),     0)  AS penalties
			FROM `tabCement Lifting` WHERE {" AND ".join(conds)}
		""", vals, as_dict=True)
		if l:
			analytics["liftings"]["total_liftings"]  = l[0].cnt or 0
			analytics["liftings"]["lifted_tons"]     = round(flt(l[0].fac_tons),   1)
			analytics["liftings"]["shortage_tons"]   = round(flt(l[0].short_tons), 1)
			analytics["liftings"]["total_penalties"] = round(flt(l[0].penalties),  2)

	if frappe.db.table_exists("tabCement Coupon"):
		analytics["coupons"]["active_count"] = frappe.db.count(
			"Cement Coupon", {"status": ["in", ["Collected", "In Custody", "Handed Over"]]}
		)
		analytics["coupons"]["used_count"] = frappe.db.count("Cement Coupon", {"status": "Used"})

	return analytics


@frappe.whitelist()
def get_liftings_by_factory(from_date=None, to_date=None):
	"""Return lifting totals grouped by factory."""
	if not frappe.db.table_exists("tabCement Lifting"):
		return []

	conds = ["docstatus < 2"]
	vals  = {}
	if from_date:
		conds.append("lifting_date >= %(from_date)s"); vals["from_date"] = from_date
	if to_date:
		conds.append("lifting_date <= %(to_date)s");   vals["to_date"]   = to_date

	return frappe.db.sql(f"""
		SELECT
			factory,
			COUNT(name)                              AS total_liftings,
			COALESCE(SUM(factory_weight),       0)   AS factory_tons,
			COALESCE(SUM(buyer_weighbridge_qty),0)   AS buyer_tons,
			COALESCE(SUM(shortage_qty),         0)   AS shortage_tons,
			COALESCE(SUM(shortage_penalty),     0)   AS total_penalties
		FROM `tabCement Lifting`
		WHERE {" AND ".join(conds)} AND factory IS NOT NULL
		GROUP BY factory
		ORDER BY factory_tons DESC
	""", vals, as_dict=True)
