import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class MedicalPricing(Document):
	def validate(self):
		self.calculate_pricing()

	def calculate_pricing(self):
		total_cost = (
			flt(self.manufacturer_price) +
			flt(self.freight) +
			flt(self.insurance) +
			flt(self.customs) +
			flt(self.inland_transport) +
			flt(self.bank_cost) +
			flt(self.warehouse_cost) +
			flt(self.handling_cost) +
			flt(self.wastage_allowance) +
			flt(self.other_costs)
		)
		self.total_cost = total_cost

		margin = flt(self.margin_percent)
		if total_cost > 0:
			self.recommended_price = total_cost * (1.0 + margin / 100.0)
		else:
			self.recommended_price = 0.0

		if not self.approved_price:
			self.approved_price = self.recommended_price
