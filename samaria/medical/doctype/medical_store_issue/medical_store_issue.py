# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

class MedicalStoreIssue(Document):
	def validate(self):
		validate_batches(self)

	def on_submit(self):
		on_submit_handler(self)

	def on_cancel(self):
		on_cancel_handler(self)


def validate_batches(doc, method=None):
	total = 0.0
	for row in doc.get("items", []):
		row_qty = flt(row.quantity)
		price = flt(row.unit_price)
		row.total_amount = row_qty * price
		total += row.total_amount

		if row.batch:
			batch_doc = frappe.get_doc("Medical Batch", row.batch)
			if batch_doc.expiry_date and getdate(batch_doc.expiry_date) < getdate(today()):
				frappe.throw(f"Batch {batch_doc.batch_no} for item {batch_doc.item_name} has expired on {batch_doc.expiry_date} and cannot be issued.")
			
			if doc.is_new() or doc.docstatus == 0:
				if flt(batch_doc.quantity) < row_qty:
					frappe.throw(f"Insufficient stock in Batch {batch_doc.batch_no}. Requested: {row_qty}, Available: {batch_doc.quantity}")

	doc.total_amount = total


def on_submit_handler(doc, method=None):
	for row in doc.get("items", []):
		if row.batch:
			batch_doc = frappe.get_doc("Medical Batch", row.batch)
			new_qty = max(0.0, flt(batch_doc.quantity) - flt(row.quantity))
			batch_doc.db_set("quantity", new_qty)

	if doc.medical_request:
		frappe.db.set_value("Medical Request", doc.medical_request, "status", "Dispatched")


def on_cancel_handler(doc, method=None):
	for row in doc.get("items", []):
		if row.batch:
			batch_doc = frappe.get_doc("Medical Batch", row.batch)
			new_qty = flt(batch_doc.quantity) + flt(row.quantity)
			batch_doc.db_set("quantity", new_qty)
