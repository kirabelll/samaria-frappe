# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class AggregateDelivery(Document):
	def validate(self):
		calculate_totals(self)

	def on_submit(self):
		on_submit_handler(self)


def calculate_totals(doc, method=None):
	loaded = flt(doc.loaded_volume)
	delivered = flt(doc.delivered_volume) if doc.delivered_volume is not None else loaded
	rate = flt(doc.transport_rate)
	agg_val = flt(doc.aggregate_value)

	# Shortage is loaded minus delivered (if delivered is recorded)
	if doc.delivered_volume is not None and doc.delivered_volume > 0:
		doc.shortage_volume = max(0.0, loaded - delivered)
		doc.gross_truck_fee = delivered * rate
	else:
		doc.shortage_volume = 0.0
		doc.gross_truck_fee = loaded * rate

	doc.shortage_deduction = doc.shortage_volume * agg_val
	doc.net_truck_payment = max(0.0, doc.gross_truck_fee - doc.shortage_deduction)


def on_submit_handler(doc, method=None):
	if doc.status == "Dispatched":
		doc.status = "Delivered" if doc.delivered_volume else "Dispatched"
