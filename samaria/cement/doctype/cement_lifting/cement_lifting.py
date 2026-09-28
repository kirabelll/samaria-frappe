# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CementLifting(Document):
	def validate(self):
		calculate_lifting(self)

	def on_submit(self):
		on_submit_handler(self)

	def on_cancel(self):
		on_cancel_handler(self)


def calculate_lifting(doc, method=None):
	fac_weight = flt(doc.factory_weight)
	buyer_weight = flt(doc.buyer_weighbridge_qty) if doc.buyer_weighbridge_qty is not None else fac_weight
	rate = flt(doc.penalty_rate_per_ton)

	if doc.buyer_weighbridge_qty is not None and doc.buyer_weighbridge_qty > 0:
		doc.shortage_qty = max(0.0, fac_weight - buyer_weight)
	else:
		doc.shortage_qty = 0.0

	doc.shortage_penalty = doc.shortage_qty * rate


def on_submit_handler(doc, method=None):
	# Deduct from Cement Purchase balance
	if doc.cement_purchase:
		purchase = frappe.get_doc("Cement Purchase", doc.cement_purchase)
		current_bal = flt(purchase.balance_remaining_tons)
		new_bal = max(0.0, current_bal - flt(doc.factory_weight))
		purchase.db_set("balance_remaining_tons", new_bal)
		if new_bal <= 0:
			purchase.db_set("status", "Exhausted")

	# Update Coupon status
	if doc.coupon:
		frappe.db.set_value("Cement Coupon", doc.coupon, {
			"status": "Used",
			"used_date": frappe.utils.today()
		})


def on_cancel_handler(doc, method=None):
	# Reverse Cement Purchase balance
	if doc.cement_purchase:
		purchase = frappe.get_doc("Cement Purchase", doc.cement_purchase)
		current_bal = flt(purchase.balance_remaining_tons)
		new_bal = current_bal + flt(doc.factory_weight)
		purchase.db_set("balance_remaining_tons", new_bal)
		if purchase.status == "Exhausted" and new_bal > 0:
			purchase.db_set("status", "Active")
