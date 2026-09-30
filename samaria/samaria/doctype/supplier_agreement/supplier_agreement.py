import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class SupplierAgreement(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_totals()

	def validate_dates(self):
		if self.valid_from and self.valid_to:
			if getdate(self.valid_to) < getdate(self.valid_from):
				frappe.throw(_("Valid To cannot be before Valid From."))

	def calculate_totals(self):
		total = 0.0
		for item in self.get("items") or []:
			base = flt(item.qty) * flt(item.unit_price)
			item.amount = base * 1.15 if item.price_type == "incl" else base
			total += item.amount
		self.total_amount = total
