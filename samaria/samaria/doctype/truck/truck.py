import frappe
from frappe.model.document import Document

class Truck(Document):
	def validate(self):
		if self.plate_no:
			self.plate_no = self.plate_no.strip().upper()
