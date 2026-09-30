import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CementPurchase(Document):
	def validate(self):
		self.calculate_amounts()
		self.set_balances()
		self.update_statuses()

	def calculate_amounts(self):
		base = flt(self.quantity_tons) * flt(self.unit_price)
		vat = base * (flt(self.vat_rate) / 100.0)
		self.vat_amount = vat
		self.total_amount = base + vat

	def set_balances(self):
		# Initialise balance_remaining only for brand-new docs
		if self.is_new():
			self.balance_remaining = flt(self.quantity_tons)

	def update_statuses(self):
		paid = flt(self.paid_amount)
		total = flt(self.total_amount)

		if paid >= total and total > 0:
			self.payment_status = "Paid"
			if self.status in ["Pending", "Checked"]:
				self.status = "Active"
		elif paid > 0:
			self.payment_status = "Partial"
		else:
			self.payment_status = "Unpaid"

		if flt(self.balance_remaining) <= 0 and self.status == "Active":
			self.status = "Exhausted"
