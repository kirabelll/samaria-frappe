# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransportAssociation(Document):
	def validate(self):
		if self.default_service_charge_percent and self.default_service_charge_percent < 0:
			frappe.throw("Default Service Charge cannot be negative")
