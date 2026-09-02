import frappe
from frappe.model.document import Document

class MedicalPricing(Document):
	def validate(self):
		self.calculate_pricing()

	def calculate_pricing(self):
		total_cost = (
			float(self.manufacturer_price or 0) +
			float(self.freight or 0) +
			float(self.insurance or 0) +
			float(self.customs or 0) +
			float(self.inland_transport or 0) +
			float(self.bank_cost or 0) +
			float(self.warehouse_cost or 0) +
			float(self.handling_cost or 0) +
			float(self.wastage_allowance or 0) +
			float(self.other_costs or 0)
		)
		self.total_cost = total_cost

		margin = float(self.margin_percent or 0)
		if total_cost > 0:
			self.recommended_price = total_cost * (1.0 + margin / 100.0)
		else:
			self.recommended_price = 0.0

		if not self.approved_price:
			self.approved_price = self.recommended_price
