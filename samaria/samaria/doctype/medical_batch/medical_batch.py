import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate, date_diff


class MedicalBatch(Document):
	def validate(self):
		self.calculate_days_to_expiry()

	def calculate_days_to_expiry(self):
		if self.expiry_date:
			self.days_to_expiry = date_diff(self.expiry_date, nowdate())
			if self.days_to_expiry <= 0:
				self.status = "Expired"

	@frappe.whitelist()
	def adjust_quantity(self, delta):
		"""Manual stock adjustment — positive delta adds, negative subtracts."""
		delta = flt(delta)
		new_qty = max(0.0, flt(self.quantity) + delta)
		self.quantity = new_qty
		self.save(ignore_permissions=True)
		return self.quantity


@frappe.whitelist()
def get_available_batches_fefo(item_code):
	"""Return Available batches for an item sorted by expiry date (FEFO)."""
	return frappe.get_all(
		"Medical Batch",
		filters={
			"item_code": item_code,
			"status": "Available",
			"quantity": [">", 0]
		},
		fields=["name", "batch_no", "expiry_date", "days_to_expiry", "quantity", "cost_price", "warehouse"],
		order_by="expiry_date asc"
	)
