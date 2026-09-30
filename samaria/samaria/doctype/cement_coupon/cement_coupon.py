import frappe
from frappe.model.document import Document


class CementCoupon(Document):
	def validate(self):
		# Ensure coupon_no is upper-cased
		if self.coupon_no:
			self.coupon_no = self.coupon_no.upper()
