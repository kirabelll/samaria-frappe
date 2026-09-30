import frappe
from frappe.model.document import Document
from frappe.utils import flt


COST_FIELDS = [
	"manufacturer_price", "freight", "insurance", "customs",
	"inland_transport", "bank_cost", "warehouse_cost",
	"handling_cost", "wastage_allowance", "other_costs"
]


class MedicalPricing(Document):
	def validate(self):
		self.calculate_pricing()

	def calculate_pricing(self):
		total_cost = sum(flt(getattr(self, f, 0)) for f in COST_FIELDS)
		self.total_cost = total_cost
		margin = flt(self.margin_percent) / 100.0
		self.recommended_price = total_cost * (1 + margin)
		if not flt(self.approved_price):
			self.approved_price = self.recommended_price
