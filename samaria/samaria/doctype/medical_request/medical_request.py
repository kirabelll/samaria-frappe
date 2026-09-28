import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate

class MedicalRequest(Document):
	def validate(self):
		self.validate_customer_license()
		self.calculate_pricing()

	def validate_customer_license(self):
		if self.customer:
			cust = frappe.get_doc("Customer", self.customer)
			license_expiry = getattr(cust, "license_expiry", None)
			if license_expiry:
				exp_date = getdate(license_expiry)
				if exp_date < getdate(nowdate()):
					frappe.msgprint(
						_("Warning: Medical License for {0} expired on {1}.").format(cust.customer_name or cust.name, license_expiry),
						alert=True
					)

	def calculate_pricing(self):
		total_count = 0
		total_amt = 0.0

		for row in getattr(self, "items", []):
			total_count += 1
			# Auto fetch price from Medical Pricing if not provided
			if not row.unit_price and row.item_code:
				pricing = frappe.get_all(
					"Medical Pricing",
					filters={"item_code": row.item_code},
					fields=["approved_price", "recommended_price"],
					order_by="effective_date desc",
					limit=1
				)
				if pricing:
					row.unit_price = pricing[0].approved_price or pricing[0].recommended_price or 0.0

			row_qty = flt(row.qty)
			row_price = flt(row.unit_price)
			row.total_amount = row_qty * row_price
			total_amt += row.total_amount

		self.total_items_count = total_count
		self.total_amount = total_amt

	@frappe.whitelist()
	def create_store_issue(self):
		"""Generates a new Medical Store Issue document from this request."""
		if self.status not in ["Approved", "Quoted", "Submitted", "Released"]:
			frappe.throw(_("Cannot create Store Issue for a cancelled or delivered request."))

		issue = frappe.new_doc("Medical Store Issue")
		issue.request = self.name
		issue.customer = self.customer
		issue.status = "Draft"
		issue.issue_date = nowdate()

		for item in getattr(self, "items", []):
			# Attempt to locate best FEFO batch
			best_batch = None
			batches = frappe.get_all(
				"Medical Batch",
				filters={
					"item_code": item.item_code,
					"status": "Available",
					"quantity": [">", 0]
				},
				fields=["name", "batch_no", "expiry_date", "quantity"],
				order_by="expiry_date asc",
				limit=1
			)
			if batches:
				best_batch = batches[0]

			issue.append("items", {
				"item_code": item.item_code,
				"batch": best_batch.name if best_batch else None,
				"batch_no": best_batch.batch_no if best_batch else None,
				"expiry_date": best_batch.expiry_date if best_batch else None,
				"qty": item.qty,
				"unit": item.unit,
				"unit_price": item.unit_price,
				"total_amount": flt(item.qty) * flt(item.unit_price)
			})

		issue.calculate_totals()
		issue.insert(ignore_permissions=True)
		self.status = "Released"
		self.save(ignore_permissions=True)
		return issue.name
