import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class MedicalStoreIssue(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_batch_stock()

	def on_submit(self):
		self.deduct_batch_stock()
		self.update_request_status()

	def on_cancel(self):
		self.restore_batch_stock()

	def calculate_totals(self):
		total = 0.0
		for item in self.get("items") or []:
			item.total_amount = flt(item.qty) * flt(item.unit_price)
			total += item.total_amount
		self.total_amount = total

	def validate_batch_stock(self):
		for item in self.get("items") or []:
			if not item.batch:
				continue
			batch = frappe.get_doc("Medical Batch", item.batch)
			if batch.status != "Available":
				frappe.throw(
					_("Batch {0} for {1} is {2} and cannot be issued.").format(
						batch.batch_no, item.item_code, batch.status
					)
				)
			if flt(item.qty) > flt(batch.quantity):
				frappe.throw(
					_("Requested qty ({0}) exceeds available stock ({1}) in batch {2}.").format(
						item.qty, batch.quantity, batch.batch_no
					)
				)

	def deduct_batch_stock(self):
		for item in self.get("items") or []:
			if item.batch:
				batch = frappe.get_doc("Medical Batch", item.batch)
				batch.quantity = max(0.0, flt(batch.quantity) - flt(item.qty))
				batch.save(ignore_permissions=True)

	def restore_batch_stock(self):
		for item in self.get("items") or []:
			if item.batch:
				batch = frappe.get_doc("Medical Batch", item.batch)
				batch.quantity = flt(batch.quantity) + flt(item.qty)
				batch.save(ignore_permissions=True)

	def update_request_status(self):
		if self.request:
			frappe.db.set_value("Medical Request", self.request, "status", "Dispatched")
