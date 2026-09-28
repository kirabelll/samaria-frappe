# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CementPenalty(Document):
	def validate(self):
		qty = flt(self.shortage_qty)
		rate = flt(self.penalty_rate)
		self.penalty_amount = qty * rate
