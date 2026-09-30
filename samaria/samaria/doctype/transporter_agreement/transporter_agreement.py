import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class TransporterAgreement(Document):
	def validate(self):
		self.validate_dates()

	def validate_dates(self):
		if self.valid_from and self.valid_to:
			if getdate(self.valid_to) < getdate(self.valid_from):
				frappe.throw(_("Valid To date cannot be before Valid From date."))
