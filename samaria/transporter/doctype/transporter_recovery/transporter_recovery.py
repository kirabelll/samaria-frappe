# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransporterRecovery(Document):
	def validate(self):
		self.pending_amount = max(0.0, (self.original_amount or 0.0) - (self.recovered_amount or 0.0))
		if self.pending_amount == 0 and self.original_amount > 0:
			self.status = "Fully Recovered"
		elif self.recovered_amount > 0 and self.pending_amount > 0:
			self.status = "Partially Recovered"
