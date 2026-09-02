import frappe
from frappe.model.document import Document

class CementLifting(Document):
	def validate(self):
		factory_wt = float(self.factory_weight or 0)
		buyer_wt = float(self.buyer_weighbridge_qty) if self.buyer_weighbridge_qty is not None else factory_wt
		
		if self.buyer_weighbridge_qty is not None:
			self.shortage_qty = max(0.0, factory_wt - buyer_wt)
		else:
			self.shortage_qty = 0.0

	def on_submit(self):
		self.update_purchase_balance()
		self.update_coupon_status()

	def on_cancel(self):
		self.reverse_purchase_balance()

	def update_purchase_balance(self):
		if self.purchase and self.factory_weight:
			purchase_doc = frappe.get_doc("Cement Purchase", self.purchase)
			current_bal = float(purchase_doc.balance_remaining or 0)
			lifted_wt = float(self.factory_weight or 0)
			new_bal = max(0.0, current_bal - lifted_wt)
			purchase_doc.balance_remaining = new_bal
			if new_bal <= 0:
				purchase_doc.status = "Exhausted"
			purchase_doc.save(ignore_permissions=True)

	def reverse_purchase_balance(self):
		if self.purchase and self.factory_weight:
			purchase_doc = frappe.get_doc("Cement Purchase", self.purchase)
			current_bal = float(purchase_doc.balance_remaining or 0)
			lifted_wt = float(self.factory_weight or 0)
			purchase_doc.balance_remaining = current_bal + lifted_wt
			if purchase_doc.status == "Exhausted" and purchase_doc.balance_remaining > 0:
				purchase_doc.status = "Active"
			purchase_doc.save(ignore_permissions=True)

	def update_coupon_status(self):
		if self.coupon:
			frappe.db.set_value("Cement Coupon", self.coupon, {
				"status": "Used",
				"used_date": self.lifting_date
			})
