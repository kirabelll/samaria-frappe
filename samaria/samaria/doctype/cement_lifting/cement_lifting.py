import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CementLifting(Document):
	def validate(self):
		self.validate_purchase_status()
		self.validate_customer_agreement()
		self.calculate_shortages()

	def on_submit(self):
		self.update_purchase_balance()
		self.update_coupon_status()

	def on_cancel(self):
		self.reverse_purchase_balance()
		self.reset_coupon_status()

	# ------------------------------------------------------------------
	def validate_purchase_status(self):
		if self.purchase:
			purchase = frappe.get_doc("Cement Purchase", self.purchase)
			if purchase.status not in ["Active", "Exhausted"]:
				frappe.throw(
					_("Cannot create lifting: Cement Purchase {0} must be Active. Current status: {1}").format(
						purchase.name, purchase.status
					)
				)
			if self.is_new() and flt(self.factory_weight) > flt(purchase.balance_remaining):
				frappe.msgprint(
					_("Warning: Lifting weight ({0} Tons) exceeds remaining purchase balance ({1} Tons).").format(
						self.factory_weight, purchase.balance_remaining
					)
				)

	def validate_customer_agreement(self):
		if self.customer:
			active = frappe.get_all(
				"Sales Agreement",
				filters={"customer": self.customer, "status": "Active"},
				limit=1
			)
			if not active:
				frappe.msgprint(
					_("Notice: No active Sales Agreement found for customer {0}.").format(self.customer),
					indicator="orange"
				)

	def calculate_shortages(self):
		factory_wt = flt(self.factory_weight)
		buyer_wt   = flt(self.buyer_weighbridge_qty) if self.buyer_weighbridge_qty is not None else factory_wt
		if self.buyer_weighbridge_qty is not None:
			self.shortage_qty = max(0.0, factory_wt - buyer_wt)
		else:
			self.shortage_qty = 0.0

	# ------------------------------------------------------------------
	def update_purchase_balance(self):
		if self.purchase and self.factory_weight:
			pur = frappe.get_doc("Cement Purchase", self.purchase)
			new_bal = max(0.0, flt(pur.balance_remaining) - flt(self.factory_weight))
			pur.balance_remaining = new_bal
			if new_bal <= 0:
				pur.status = "Exhausted"
			pur.save(ignore_permissions=True)

	def reverse_purchase_balance(self):
		if self.purchase and self.factory_weight:
			pur = frappe.get_doc("Cement Purchase", self.purchase)
			pur.balance_remaining = flt(pur.balance_remaining) + flt(self.factory_weight)
			if pur.status == "Exhausted" and pur.balance_remaining > 0:
				pur.status = "Active"
			pur.save(ignore_permissions=True)

	def update_coupon_status(self):
		if self.coupon:
			frappe.db.set_value("Cement Coupon", self.coupon, {
				"status": "Used",
				"used_date": self.lifting_date
			})

	def reset_coupon_status(self):
		if self.coupon:
			frappe.db.set_value("Cement Coupon", self.coupon, {
				"status": "In Custody",
				"used_date": None
			})
