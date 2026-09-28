import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class AggregateDelivery(Document):
	def validate(self):
		self.resolve_agreement_prices()
		self.calculate_financials()
		self.validate_status_transitions()

	def resolve_agreement_prices(self):
		"""Auto-resolve prices from Sales Agreement and Supplier Agreement if not set."""
		dispatch_date = getdate(self.dispatch_date) if self.dispatch_date else getdate()

		# Resolve Customer Price from Sales Agreement if empty
		if not self.customer_price and self.customer and self.item:
			cust_agreements = frappe.get_all(
				"Sales Agreement",
				filters={
					"customer": self.customer,
					"status": ["not in", ["Void", "Cancelled"]],
					"valid_from": ["<=", dispatch_date],
					"valid_to": [">=", dispatch_date]
				},
				fields=["name"],
				order_by="creation desc",
				limit=1
			)
			if cust_agreements:
				agreement_doc = frappe.get_doc("Sales Agreement", cust_agreements[0].name)
				for item_row in getattr(agreement_doc, "items", []):
					if item_row.item == self.item or getattr(item_row, "item_code", None) == self.item:
						self.customer_price = float(item_row.unit_price or 0)
						break

		# Resolve Supplier Aggregate Rate from Supplier Agreement if empty
		if not self.aggregate_value and self.supplier and self.item:
			supp_agreements = frappe.get_all(
				"Supplier Agreement",
				filters={
					"supplier": self.supplier,
					"status": ["not in", ["Void", "Cancelled"]],
					"valid_from": ["<=", dispatch_date],
					"valid_to": [">=", dispatch_date]
				},
				fields=["name"],
				order_by="creation desc",
				limit=1
			)
			if supp_agreements:
				agreement_doc = frappe.get_doc("Supplier Agreement", supp_agreements[0].name)
				for item_row in getattr(agreement_doc, "items", []):
					if item_row.item == self.item or getattr(item_row, "item_code", None) == self.item:
						self.aggregate_value = float(item_row.unit_price or 0)
						break

		# Default customer price to aggregate value if still 0
		if not self.customer_price and self.aggregate_value:
			self.customer_price = self.aggregate_value

	def calculate_financials(self):
		loaded = float(self.loaded_volume or 0)
		delivered = float(self.delivered_volume) if self.delivered_volume is not None else loaded
		rate = float(self.transport_rate or 0)
		supp_rate = float(self.aggregate_value or 0)
		cust_rate = float(self.customer_price or self.aggregate_value or 0)

		# Truck capacity cap
		capacity = float(self.truck_capacity or 0)
		billable_volume = capacity if (capacity > 0 and loaded > capacity) else loaded
		self.billable_volume = billable_volume

		# Shortage calculation
		if self.delivered_volume is not None:
			self.shortage_volume = max(0.0, loaded - delivered)
		else:
			self.shortage_volume = 0.0

		# Transporter fee & shortage deduction
		self.gross_truck_fee = billable_volume * rate
		self.shortage_deduction = self.shortage_volume * supp_rate
		self.net_truck_payment = max(0.0, self.gross_truck_fee - self.shortage_deduction)

		# Customer & Supplier amounts
		self.customer_receivable = loaded * cust_rate
		self.supplier_payable = delivered * supp_rate
		self.net_profit_amount = self.customer_receivable - self.supplier_payable - self.gross_truck_fee

	def validate_status_transitions(self):
		if self.delivered_volume is not None and self.status == "Dispatched":
			self.status = "Delivered"
