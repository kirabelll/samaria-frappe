import frappe
from frappe.model.document import Document

class AggregateDelivery(Document):
	def validate(self):
		self.calculate_financials()

	def calculate_financials(self):
		loaded = float(self.loaded_volume or 0)
		delivered = float(self.delivered_volume) if self.delivered_volume is not None else loaded
		rate = float(self.transport_rate or 0)
		supp_rate = float(self.aggregate_value or 0)
		cust_rate = float(self.customer_price or self.aggregate_value or 0)
		
		# Truck capacity cap
		capacity = float(self.truck_capacity or 0)
		billable_volume = capacity if (capacity > 0 and loaded > capacity) else loaded

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
