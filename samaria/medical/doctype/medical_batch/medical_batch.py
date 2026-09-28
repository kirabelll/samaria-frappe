# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class MedicalBatch(Document):
	def validate(self):
		if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			if self.status != "Expired" and self.status != "Recalled":
				self.status = "Expired"
