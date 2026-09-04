import frappe
from frappe.model.document import Document

class CementPurchase(Document):
	def validate(self):
		qty = float(self.quantity_tons or 0)
		price = float(self.unit_price or 0)
		base_total = qty * price

		vat_r = float(self.vat_rate or 0)
		vat_amt = (vat_r / 100.0) * base_total
		self.vat_amount = vat_amt
		self.total_amount = base_total + vat_amt

		# If new doc, initialize balance_remaining to quantity_tons
		if self.is_new() or self.balance_remaining is None:
			self.balance_remaining = qty

		# Update payment status
		paid = float(self.paid_amount or 0)
		if paid >= self.total_amount and self.total_amount > 0:
			self.payment_status = "Paid"
		elif paid > 0:
			self.payment_status = "Partial"
		else:
			self.payment_status = "Unpaid"
