import frappe
from frappe.model.document import Document

class SupplierAgreement(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_dates()

	def calculate_totals(self):
		total = 0.0
		for item in self.get("items", []):
			qty = float(item.qty or 0)
			unit_price = float(item.unit_price or 0)
			
			if item.price_type == "incl":
				item.amount = qty * unit_price * 1.15
			else:
				item.amount = qty * unit_price
			
			total += item.amount
		self.total_amount = total

	def validate_dates(self):
		if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
			frappe.throw("Valid To date cannot be earlier than Valid From date")
