import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

class MedicalStoreIssue(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_batch_stock()

	def calculate_totals(self):
		total = 0.0
		for item in getattr(self, "items", []):
			item_qty = flt(item.qty)
			item_price = flt(item.unit_price)
			item.total_amount = item_qty * item_price
			total += item.total_amount

		self.total_amount = total

	def validate_batch_stock(self):
		for item in getattr(self, "items", []):
			if item.batch:
				batch_doc = frappe.get_doc("Medical Batch", item.batch)
				if batch_doc.status != "Available":
					frappe.throw(_("Batch {0} for item {1} is {2} and cannot be issued.").format(batch_doc.batch_no, item.item_code, batch_doc.status))
				if flt(item.qty) > flt(batch_doc.quantity):
					frappe.throw(_("Requested quantity ({0}) exceeds available batch stock ({1}) for batch {2}.").format(item.qty, batch_doc.quantity, batch_doc.batch_no))

	def on_submit(self):
		self.deduct_batch_stock()
		self.update_request_status()

	def on_cancel(self):
		self.restore_batch_stock()

	def deduct_batch_stock(self):
		for item in getattr(self, "items", []):
			if item.batch:
				batch_doc = frappe.get_doc("Medical Batch", item.batch)
				new_qty = max(0.0, flt(batch_doc.quantity) - flt(item.qty))
				batch_doc.quantity = new_qty
				batch_doc.save(ignore_permissions=True)

	def restore_batch_stock(self):
		for item in getattr(self, "items", []):
			if item.batch:
				batch_doc = frappe.get_doc("Medical Batch", item.batch)
				batch_doc.quantity = flt(batch_doc.quantity) + flt(item.qty)
				batch_doc.save(ignore_permissions=True)

	def update_request_status(self):
		if self.request:
			frappe.db.set_value("Medical Request", self.request, "status", "Dispatched")
