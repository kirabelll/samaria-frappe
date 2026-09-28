# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CementPurchase(Document):
	def validate(self):
		qty = flt(self.quantity_tons)
		price = flt(self.unit_price)
		self.total_amount = qty * price

		# If balance remaining is not initialized, set it to total quantity
		if self.is_new() or self.balance_remaining_tons is None:
			self.balance_remaining_tons = qty

		paid = flt(self.paid_amount)
		if paid >= self.total_amount and self.total_amount > 0:
			self.payment_status = "Fully Paid"
		elif paid > 0:
			self.payment_status = "Partially Paid"
		else:
			self.payment_status = "Unpaid"

		if self.balance_remaining_tons <= 0 and qty > 0:
			self.status = "Exhausted"
