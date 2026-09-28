# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TruckPayment(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		gross = flt(self.total_gross_fee)
		shortage = flt(self.total_shortage_deduction)
		self.total_net_payment = max(0.0, gross - shortage)

		assoc = flt(self.association_deduction)
		recovery = flt(self.recovery_deduction)

		self.final_payable = max(0.0, self.total_net_payment - assoc - recovery)
