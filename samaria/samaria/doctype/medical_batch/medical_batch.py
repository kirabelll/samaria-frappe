import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff

class MedicalBatch(Document):
	def validate(self):
		if self.expiry_date:
			today = getdate(nowdate())
			exp = getdate(self.expiry_date)
			diff = date_diff(exp, today)
			self.days_to_expiry = diff
			if diff <= 0:
				self.status = "Expired"
			elif diff <= 90 and self.status == "Available":
				# Near expiry flag
				pass
