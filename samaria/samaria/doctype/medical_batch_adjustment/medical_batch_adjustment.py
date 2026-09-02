import frappe
from frappe.model.document import Document

class MedicalBatchAdjustment(Document):
	def on_submit(self):
		for row in self.get("items", []):
			if row.batch:
				frappe.db.set_value("Medical Batch", row.batch, "quantity", float(row.adjusted_qty or 0))

	def on_cancel(self):
		for row in self.get("items", []):
			if row.batch:
				frappe.db.set_value("Medical Batch", row.batch, "quantity", float(row.current_qty or 0))
