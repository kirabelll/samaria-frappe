import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CementWeighbridge(Document):
	def validate(self):
		self.net_weight = max(0.0, flt(self.gross_weight) - flt(self.tare_weight))
