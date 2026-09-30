# -*- coding: utf-8 -*-
"""
Samaria Medical API
FEFO batch query, store issue creation, expiry tracking.
Frappe v15
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate, add_days


@frappe.whitelist()
def get_fefo_batches(item_code, required_qty=None):
	"""Return available batches for an item in FEFO order (earliest expiry first)."""
	if not frappe.db.table_exists("tabMedical Batch"):
		return []

	batches = frappe.get_all(
		"Medical Batch",
		filters={
			"item_code": item_code,
			"status": "Available",
			"quantity": [">", 0]
		},
		fields=["name", "batch_no", "expiry_date", "days_to_expiry", "quantity", "cost_price", "warehouse"],
		order_by="expiry_date asc"
	)

	if required_qty:
		required_qty = flt(required_qty)
		allocated = []
		remaining = required_qty
		for b in batches:
			if remaining <= 0:
				break
			take = min(flt(b.quantity), remaining)
			allocated.append({**b, "allocated_qty": take})
			remaining -= take
		return allocated

	return batches


@frappe.whitelist()
def create_store_issue_from_request(request_id):
	"""Programmatically create a Medical Store Issue from a Medical Request using FEFO."""
	req = frappe.get_doc("Medical Request", request_id)
	if req.status not in ["Submitted", "Quoted", "Approved", "Released"]:
		frappe.throw(_("Cannot create Store Issue for request with status: {0}").format(req.status))

	issue = frappe.new_doc("Medical Store Issue")
	issue.request       = req.name
	issue.customer      = req.customer
	issue.issue_date    = nowdate()
	issue.status        = "Issued"
	issue.issued_by_user = frappe.session.user

	for item in req.get("items") or []:
		batches = frappe.get_all(
			"Medical Batch",
			filters={"item_code": item.item_code, "status": "Available", "quantity": [">", 0]},
			fields=["name", "batch_no", "expiry_date", "cost_price"],
			order_by="expiry_date asc",
			limit=1
		)
		pricing = frappe.get_all(
			"Medical Pricing",
			filters={"item_code": item.item_code},
			fields=["approved_price", "recommended_price"],
			order_by="effective_date desc",
			limit=1
		)
		unit_price = flt(item.unit_price)
		if not unit_price and pricing:
			unit_price = flt(pricing[0].approved_price) or flt(pricing[0].recommended_price)

		issue.append("items", {
			"item_code":    item.item_code,
			"item_name":    item.item_name,
			"batch":        batches[0].name        if batches else None,
			"batch_no":     batches[0].batch_no    if batches else None,
			"expiry_date":  batches[0].expiry_date if batches else None,
			"qty":          flt(item.qty),
			"unit":         item.unit,
			"unit_price":   unit_price,
			"total_amount": flt(item.qty) * unit_price
		})

	issue.insert(ignore_permissions=True)
	frappe.db.set_value("Medical Request", request_id, "status", "Released")
	return issue.name


@frappe.whitelist()
def get_expiring_batches_report(days_threshold=90):
	"""Return batches expiring within `days_threshold` days from today."""
	if not frappe.db.table_exists("tabMedical Batch"):
		return []

	cutoff = add_days(nowdate(), int(days_threshold))
	return frappe.get_all(
		"Medical Batch",
		filters={
			"status": "Available",
			"expiry_date": ["between", [nowdate(), cutoff]],
			"quantity": [">", 0]
		},
		fields=["name", "batch_no", "item_code", "item_name",
				"expiry_date", "days_to_expiry", "quantity", "cost_price", "warehouse"],
		order_by="expiry_date asc"
	)


@frappe.whitelist()
def get_medical_inventory_summary():
	"""Return inventory value and status breakdown for the Medical division."""
	if not frappe.db.table_exists("tabMedical Batch"):
		return {}

	rows = frappe.db.sql("""
		SELECT
			status,
			COUNT(name)                                        AS batch_count,
			COALESCE(SUM(quantity),               0)          AS total_qty,
			COALESCE(SUM(quantity * cost_price),  0)          AS total_value
		FROM `tabMedical Batch`
		GROUP BY status
	""", as_dict=True)

	summary = {r.status: {"count": r.batch_count, "qty": flt(r.total_qty), "value": round(flt(r.total_value), 2)} for r in rows}
	near_expiry = frappe.db.count(
		"Medical Batch",
		{"status": "Available", "expiry_date": ["between", [nowdate(), add_days(nowdate(), 90)]]}
	)
	summary["_near_expiry_count"] = near_expiry
	return summary
