# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CementWeighbridge(Document):
	def validate(self):
		gross = flt(self.gross_weight)
		tare = flt(self.tare_weight)
		self.net_weight = max(0.0, gross - tare)
