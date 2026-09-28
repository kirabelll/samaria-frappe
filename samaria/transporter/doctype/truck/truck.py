# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Truck(Document):
	def validate(self):
		if self.plate_no:
			self.plate_no = self.plate_no.strip().upper()
