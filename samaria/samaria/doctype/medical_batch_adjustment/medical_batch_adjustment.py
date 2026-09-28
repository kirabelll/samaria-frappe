import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class MedicalBatchAdjustment(Document):
	def on_submit(self):
		for row in getattr(self, "items", []):
			if row.batch:
				new_qty = flt(row.adjusted_qty)
				frappe.db.set_value("Medical Batch", row.batch, "quantity", new_qty)
				if new_qty <= 0 and getattr(row, "reason", "") in ["Damaged", "Expired", "Recalled"]:
					frappe.db.set_value("Medical Batch", row.batch, "status", getattr(row, "reason", "Damaged"))

	def on_cancel(self):
		for row in getattr(self, "items", []):
			if row.batch:
				frappe.db.set_value("Medical Batch", row.batch, "quantity", flt(row.current_qty))
				frappe.db.set_value("Medical Batch", row.batch, "status", "Available")
