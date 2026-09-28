# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, getdate

@frappe.whitelist()
def get_fefo_batches(item_code, required_qty=None):
	"""
	Fetch available batches for an item sorted by Expiry Date ASC (FEFO: First Expiry First Out).
	"""
	filters = {
		"item_code": item_code,
		"status": "Available",
		"quantity": [">", 0],
		"expiry_date": [">", today()]
	}

	batches = frappe.get_all(
		"Medical Batch",
		filters=filters,
		fields=["name", "batch_no", "expiry_date", "quantity", "cost_price", "warehouse"],
		order_by="expiry_date asc"
	)
	return batches


@frappe.whitelist()
def create_store_issue_from_request(request_id):
	"""
	Auto-creates a Medical Store Issue doc pre-filling FEFO batches from the Medical Request.
	"""
	request_doc = frappe.get_doc("Medical Request", request_id)
	issue = frappe.new_doc("Medical Store Issue")
	issue.customer = request_doc.customer
	issue.medical_request = request_doc.name
	issue.issued_date = frappe.utils.now_datetime()
	issue.status = "Issued"

	for row in request_doc.items:
		needed_qty = flt(row.quantity)
		batches = get_fefo_batches(row.item_code)

		for b in batches:
			if needed_qty <= 0:
				break
			avail = flt(b.quantity)
			alloc = min(avail, needed_qty)
			
			# Fetch pricing
			approved_price = frappe.db.get_value("Medical Pricing", {"item_code": row.item_code}, "approved_price") or b.cost_price or 0

			issue.append("items", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"batch": b.name,
				"batch_no": b.batch_no,
				"expiry_date": b.expiry_date,
				"quantity": alloc,
				"unit_price": approved_price,
				"total_amount": alloc * approved_price
			})
			needed_qty -= alloc

	issue.insert(ignore_permissions=True)
	return issue.name


@frappe.whitelist()
def get_expiring_batches_report(days_threshold=90):
	"""
	Lists all batches expiring within the specified days threshold.
	"""
	future_date = frappe.utils.add_days(today(), int(days_threshold))
	batches = frappe.get_all(
		"Medical Batch",
		filters={
			"status": "Available",
			"quantity": [">", 0],
			"expiry_date": ["between", [today(), future_date]]
		},
		fields=["name", "item_code", "item_name", "batch_no", "expiry_date", "quantity", "warehouse"],
		order_by="expiry_date asc"
	)
	return batches
