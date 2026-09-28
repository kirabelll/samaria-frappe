# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def get_factory_balances():
	"""
	Returns total active quota vs remaining balance per factory.
	"""
	data = frappe.db.sql("""
		SELECT 
			factory,
			SUM(quantity_tons) as total_purchased,
			SUM(balance_remaining_tons) as total_remaining
		FROM `tabCement Purchase`
		WHERE status = 'Active'
		GROUP BY factory
	""", as_dict=True)
	return data


@frappe.whitelist()
def get_cement_analytics():
	"""
	Summary statistics for Cement dashboard.
	"""
	purchased = frappe.db.sql("""
		SELECT 
			COALESCE(SUM(quantity_tons), 0) as purchased_tons,
			COALESCE(SUM(balance_remaining_tons), 0) as remaining_tons,
			COALESCE(SUM(total_amount), 0) as total_spent
		FROM `tabCement Purchase`
		WHERE status != 'Cancelled'
	""", as_dict=True)[0]

	lifted = frappe.db.sql("""
		SELECT 
			COALESCE(SUM(factory_weight), 0) as lifted_tons,
			COALESCE(SUM(shortage_qty), 0) as shortage_tons,
			COALESCE(SUM(shortage_penalty), 0) as total_penalties
		FROM `tabCement Lifting`
		WHERE docstatus = 1
	""", as_dict=True)[0]

	coupons_active = frappe.db.count("Cement Coupon", {"status": ["in", ["Collected", "In Custody", "Handed Over"]]})

	return {
		"total_purchased_tons": flt(purchased.purchased_tons, 2),
		"total_remaining_tons": flt(purchased.remaining_tons, 2),
		"total_lifted_tons": flt(lifted.lifted_tons, 2),
		"total_shortage_tons": flt(lifted.shortage_tons, 2),
		"total_penalties_etb": flt(lifted.total_penalties, 2),
		"active_coupons": coupons_active
	}
