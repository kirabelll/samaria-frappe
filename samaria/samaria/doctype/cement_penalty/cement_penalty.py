import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CementPenalty(Document):
	def validate(self):
		# Auto-calculate penalty from qty × rate if amount not yet set
		if flt(self.shortage_qty) > 0 and flt(self.penalty_rate) > 0:
			if not flt(self.penalty_amount):
				self.penalty_amount = flt(self.shortage_qty) * flt(self.penalty_rate)

		# Auto-update recovery status
		recovered = flt(self.recovered_amount)
		penalty   = flt(self.penalty_amount)
		if recovered >= penalty and penalty > 0:
			self.recovery_status = "Recovered"
		elif recovered > 0:
			self.recovery_status = "Deducted"
		else:
			if self.recovery_status not in ["Waived"]:
				self.recovery_status = "Pending"
