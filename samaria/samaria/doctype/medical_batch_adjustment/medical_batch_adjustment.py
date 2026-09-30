import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MedicalBatchAdjustment(Document):
	def on_submit(self):
		for item in self.get("items") or []:
			if not item.batch:
				continue
			batch = frappe.get_doc("Medical Batch", item.batch)
			batch.quantity = flt(item.adjusted_qty)
			# Write-off status rules
			if flt(item.adjusted_qty) <= 0:
				if self.reason == "Expired Goods Write-off":
					batch.status = "Expired"
				elif self.reason == "Damaged / Broken Ampoules":
					batch.status = "Damaged"
				elif self.reason == "Recall Adjustment":
					batch.status = "Recalled"
			batch.save(ignore_permissions=True)

	def on_cancel(self):
		for item in self.get("items") or []:
			if not item.batch:
				continue
			batch = frappe.get_doc("Medical Batch", item.batch)
			batch.quantity = flt(item.current_qty)
			batch.status   = "Available"
			batch.save(ignore_permissions=True)
