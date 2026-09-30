import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TransporterRecovery(Document):
	def validate(self):
		self.pending_amount = max(0.0, flt(self.original_amount) - flt(self.recovered_amount))
		recovered = flt(self.recovered_amount)
		original  = flt(self.original_amount)
		if recovered >= original and original > 0:
			self.status = "Recovered"
		elif recovered > 0:
			self.status = "Partial"
		elif self.status not in ["Written_Off"]:
			self.status = "Open"
