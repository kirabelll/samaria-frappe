# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MedicalPricing(Document):
	def validate(self):
		self.calculate_pricing()

	def calculate_pricing(self):
		cost_elements = [
			self.manufacturer_price,
			self.freight,
			self.insurance,
			self.customs,
			self.inland_transport,
			self.bank_cost,
			self.warehouse_cost,
			self.handling_cost,
			self.wastage_allowance,
			self.other_costs
		]
		self.total_cost = sum([flt(c) for c in cost_elements])

		margin = flt(self.margin_percent)
		self.recommended_price = self.total_cost * (1.0 + margin / 100.0)

		if not self.approved_price or self.approved_price == 0:
			self.approved_price = self.recommended_price
