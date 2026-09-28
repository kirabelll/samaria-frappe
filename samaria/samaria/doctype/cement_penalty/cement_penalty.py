import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class CementPenalty(Document):
	def validate(self):
		qty = flt(self.shortage_qty)
		rate = flt(self.penalty_rate)
		if qty > 0 and rate > 0 and not self.penalty_amount:
			self.penalty_amount = qty * rate
		
		# Auto-update recovery status
		recovered = flt(self.recovered_amount)
		total = flt(self.penalty_amount)
		if recovered >= total and total > 0:
			self.recovery_status = "Recovered"
		elif recovered > 0:
			self.recovery_status = "Deducted"
		elif self.recovery_status not in ["Waived", "Written_Off"]:
			self.recovery_status = "Pending"
