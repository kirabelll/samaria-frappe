import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class TransporterRecovery(Document):
	def validate(self):
		orig = flt(self.original_amount)
		rec = flt(self.recovered_amount)
		self.pending_amount = max(0.0, orig - rec)

		if self.pending_amount == 0 and orig > 0:
			self.status = "Recovered"
		elif rec > 0:
			self.status = "Partial"
		elif self.status not in ["Written_Off"]:
			self.status = "Open"
