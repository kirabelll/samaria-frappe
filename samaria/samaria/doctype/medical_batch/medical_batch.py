import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, flt

class MedicalBatch(Document):
	def validate(self):
		if self.expiry_date:
			today = getdate(nowdate())
			exp = getdate(self.expiry_date)
			diff = date_diff(exp, today)
			self.days_to_expiry = diff
			if diff <= 0:
				self.status = "Expired"
			elif diff <= 90 and self.status == "Available":
				# Near expiry - keep available but flag
				pass

	@frappe.whitelist()
	def adjust_quantity(self, delta, reason="Adjustment"):
		"""Adjusts batch stock quantity."""
		new_qty = max(0.0, flt(self.quantity) + flt(delta))
		self.quantity = new_qty
		if new_qty == 0 and self.status == "Available":
			# keep available or empty
			pass
		self.save(ignore_permissions=True)
		return self.quantity

@frappe.whitelist()
def get_available_batches_fefo(item_code, warehouse=None):
	"""Returns available batches sorted by expiry date ascending (FEFO)."""
	filters = {
		"item_code": item_code,
		"status": "Available",
		"quantity": [">", 0]
	}
	if warehouse:
		filters["warehouse"] = warehouse

	return frappe.get_all(
		"Medical Batch",
		filters=filters,
		fields=["name", "batch_no", "expiry_date", "quantity", "cost_price", "warehouse", "days_to_expiry"],
		order_by="expiry_date asc"
	)
