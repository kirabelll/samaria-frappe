import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class CementPurchase(Document):
	def validate(self):
		qty = flt(self.quantity_tons)
		price = flt(self.unit_price)
		base_total = qty * price

		vat_r = flt(self.vat_rate)
		vat_amt = (vat_r / 100.0) * base_total
		self.vat_amount = vat_amt
		self.total_amount = base_total + vat_amt

		# If new doc, initialize balance_remaining to quantity_tons
		if self.is_new() or self.balance_remaining is None:
			self.balance_remaining = qty

		# Update payment status
		paid = flt(self.paid_amount)
		if paid >= self.total_amount and self.total_amount > 0:
			self.payment_status = "Paid"
			if self.status == "Pending" or self.status == "Checked":
				self.status = "Active"
		elif paid > 0:
			self.payment_status = "Partial"
		else:
			self.payment_status = "Unpaid"

		# If balance remaining reaches zero
		if flt(self.balance_remaining) <= 0 and not self.is_new():
			self.status = "Exhausted"
		elif flt(self.balance_remaining) > 0 and self.payment_status == "Paid" and self.status == "Exhausted":
			self.status = "Active"
