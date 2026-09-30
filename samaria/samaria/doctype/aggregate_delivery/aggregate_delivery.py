import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class AggregateDelivery(Document):
	def validate(self):
		self.resolve_agreement_prices()
		self.calculate_financials()
		self.validate_status_transitions()

	def on_submit(self):
		# Status guard: only submitted records should be Delivered or Verified
		if self.status == "Dispatched":
			self.status = "Delivered"
			self.db_set("status", "Delivered")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	# ------------------------------------------------------------------
	# Price auto-resolution from Sales / Supplier Agreements
	# ------------------------------------------------------------------
	def resolve_agreement_prices(self):
		dispatch_date = getdate(self.dispatch_date) if self.dispatch_date else getdate()

		# Customer price from active Sales Agreement
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
					if item_row.item_code == self.item:
						self.customer_price = flt(item_row.unit_price)
						break

		# Supplier aggregate rate from active Supplier Agreement
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
					if item_row.item_code == self.item:
						self.aggregate_value = flt(item_row.unit_price)
						break

		# Fallback: customer price defaults to aggregate value
		if not self.customer_price and self.aggregate_value:
			self.customer_price = self.aggregate_value

	# ------------------------------------------------------------------
	# Core financial calculations
	# ------------------------------------------------------------------
	def calculate_financials(self):
		loaded = flt(self.loaded_volume)
		delivered = flt(self.delivered_volume) if self.delivered_volume is not None else loaded
		rate = flt(self.transport_rate)
		supp_rate = flt(self.aggregate_value)
		cust_rate = flt(self.customer_price) or supp_rate

		# Billable volume capped at truck capacity
		capacity = flt(self.truck_capacity)
		self.billable_volume = capacity if (capacity > 0 and loaded > capacity) else loaded

		# Shortage
		if self.delivered_volume is not None:
			self.shortage_volume = max(0.0, loaded - delivered)
		else:
			self.shortage_volume = 0.0

		# Transport payments
		self.gross_truck_fee = self.billable_volume * rate
		self.shortage_deduction = self.shortage_volume * supp_rate
		self.net_truck_payment = max(0.0, self.gross_truck_fee - self.shortage_deduction)

		# Commercial amounts
		self.customer_receivable = loaded * cust_rate
		self.supplier_payable = delivered * supp_rate
		self.net_profit_amount = self.customer_receivable - self.supplier_payable - self.gross_truck_fee

	def validate_status_transitions(self):
		if self.delivered_volume is not None and self.status == "Dispatched":
			self.status = "Delivered"
