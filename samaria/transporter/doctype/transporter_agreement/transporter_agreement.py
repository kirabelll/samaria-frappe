# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class TransporterAgreement(Document):
	def validate(self):
		if self.valid_from and self.valid_to:
			if getdate(self.valid_to) < getdate(self.valid_from):
				frappe.throw("Valid To date cannot be before Valid From date")
		
		# Auto calculate category pricing total
		for row in self.get("category_pricing", []):
			if row.holding_capacity and row.unit_price:
				row.total_price = row.holding_capacity * row.unit_price
