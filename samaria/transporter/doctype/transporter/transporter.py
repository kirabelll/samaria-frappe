# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Transporter(Document):
	def validate(self):
		if not self.code:
			self.code = self.name
