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
			license_expiry = getattr(cust, "custom_license_expiry", None) or getattr(cust, "license_expiry", None)
			if license_expiry and getdate(license_expiry) < getdate(nowdate()):
				frappe.msgprint(
					_("Customer {0} license expired on {1}. Please verify before proceeding.").format(
						self.customer, license_expiry
					),
					indicator="orange"
				)

	def calculate_pricing(self):
		total_items = 0
		total_amount = 0.0
		for item in self.get("items") or []:
			# Auto-fetch price from Medical Pricing if not set
			if not flt(item.unit_price) and item.item_code:
				pricing = frappe.get_all(
					"Medical Pricing",
					filters={"item_code": item.item_code},
					fields=["approved_price", "recommended_price"],
					order_by="effective_date desc",
					limit=1
				)
				if pricing:
					item.unit_price = flt(pricing[0].approved_price) or flt(pricing[0].recommended_price)

			item.total_amount = flt(item.qty) * flt(item.unit_price)
			total_items += 1
			total_amount += item.total_amount

		self.total_items_count = total_items
		self.total_amount = total_amount

	@frappe.whitelist()
	def create_store_issue(self):
		"""Create a Medical Store Issue from this request using FEFO batch allocation."""
		if self.status not in ["Submitted", "Quoted", "Approved", "Released"]:
			frappe.throw(_("Store Issue can only be created for Submitted, Quoted, Approved or Released requests."))

		issue = frappe.new_doc("Medical Store Issue")
		issue.request   = self.name
		issue.customer  = self.customer
		issue.issue_date = nowdate()
		issue.status    = "Issued"
		issue.issued_by_user = frappe.session.user

		for item in self.get("items") or []:
			# FEFO: pick earliest-expiry available batch with sufficient qty
			batches = frappe.get_all(
				"Medical Batch",
				filters={
					"item_code": item.item_code,
					"status": "Available",
					"quantity": [">", 0]
				},
				fields=["name", "batch_no", "expiry_date", "quantity", "cost_price"],
				order_by="expiry_date asc",
				limit=1
			)
			batch_name = batches[0].name if batches else None
			batch_no   = batches[0].batch_no if batches else None
			expiry     = batches[0].expiry_date if batches else None

			issue.append("items", {
				"item_code":   item.item_code,
				"item_name":   item.item_name,
				"batch":       batch_name,
				"batch_no":    batch_no,
				"expiry_date": expiry,
				"qty":         flt(item.qty),
				"unit":        item.unit,
				"unit_price":  flt(item.unit_price),
				"total_amount": flt(item.qty) * flt(item.unit_price)
			})

		issue.insert(ignore_permissions=True)
		frappe.db.set_value("Medical Request", self.name, "status", "Released")
		return issue.name
