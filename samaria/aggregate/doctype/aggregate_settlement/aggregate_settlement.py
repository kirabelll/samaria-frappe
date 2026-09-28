# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class AggregateSettlement(Document):
	def validate(self):
		self.calculate_settlement()

	def calculate_settlement(self):
		total_dispatches = len(self.get("deliveries", []))
		total_loaded = 0.0
		total_delivered = 0.0
		total_shortage = 0.0
		total_gross = 0.0
		total_shortage_ded = 0.0
		total_net = 0.0

		for row in self.get("deliveries", []):
			total_loaded += flt(row.loaded_volume)
			total_delivered += flt(row.delivered_volume)
			total_shortage += flt(row.shortage_volume)
			total_gross += flt(row.gross_fee)
			total_shortage_ded += flt(row.shortage_deduction)
			total_net += flt(row.net_payment)

		self.total_dispatches = total_dispatches
		self.total_loaded_volume = total_loaded
		self.total_delivered_volume = total_delivered
		self.total_shortage = total_shortage
		self.total_gross_fee = total_gross
		self.total_shortage_deduction = total_shortage_ded
		self.total_net_payment = total_net

		# Association charge calculation
		assoc_rate = flt(self.association_rate)
		self.association_amount = (total_net * assoc_rate / 100.0) if assoc_rate > 0 else 0.0

		recovery = flt(self.recovery_deduction)
		self.final_payable = max(0.0, total_net - self.association_amount - recovery)

	def on_submit(self):
		# Mark deliveries as Settled
		for row in self.get("deliveries", []):
			if row.delivery:
				frappe.db.set_value("Aggregate Delivery", row.delivery, "status", "Settled")
