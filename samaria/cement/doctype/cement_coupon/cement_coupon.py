# Copyright (c) 2026, Samaria ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CementCoupon(Document):
	def validate(self):
		validate_coupon(self)


def validate_coupon(doc, method=None):
	if doc.coupon_no:
		doc.coupon_no = doc.coupon_no.strip().upper()
