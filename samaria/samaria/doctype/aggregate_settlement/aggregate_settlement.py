import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AggregateSettlement(Document):
	def validate(self):
		self.calculate_totals()

	def on_submit(self):
		self.mark_deliveries_settled()

	def on_cancel(self):
		self.unmark_deliveries_settled()

	# ------------------------------------------------------------------
	# Totals aggregation
	# ------------------------------------------------------------------
	def calculate_totals(self):
		total_dispatches = 0
		total_loaded = 0.0
		total_delivered = 0.0
		total_shortage = 0.0
		total_gross = 0.0
		total_deduction = 0.0
		total_net = 0.0

		for item in self.get("items") or []:
			total_dispatches += 1
			total_loaded += flt(item.loaded_volume)
			total_delivered += flt(item.delivered_volume)
			total_shortage += flt(item.shortage_volume)
			total_gross += flt(item.gross_truck_fee)
			total_deduction += flt(item.shortage_deduction)
			total_net += flt(item.net_truck_payment)

		self.total_dispatches = total_dispatches
		self.total_loaded_volume = total_loaded
		self.total_delivered_volume = total_delivered
		self.total_shortage_volume = total_shortage
		self.total_gross_fee = total_gross
		self.total_shortage_deduction = total_deduction
		self.total_net_payment = total_net

		# Association service charge
		if self.association_charge_enabled and flt(self.association_rate) > 0:
			self.association_amount = (flt(self.association_rate) / 100.0) * total_net
		else:
			self.association_amount = 0.0

		self.final_payable = max(
			0.0,
			total_net - flt(self.association_amount) - flt(self.recovery_deduction)
		)

	# ------------------------------------------------------------------
	# Delivery status updates
	# ------------------------------------------------------------------
	def mark_deliveries_settled(self):
		for item in self.get("items") or []:
			if item.delivery:
				frappe.db.set_value("Aggregate Delivery", item.delivery, "status", "Settled")

	def unmark_deliveries_settled(self):
		for item in self.get("items") or []:
			if item.delivery:
				frappe.db.set_value("Aggregate Delivery", item.delivery, "status", "Verified")

	# ------------------------------------------------------------------
	# Whitelisted method — called from JS button
	# ------------------------------------------------------------------
	@frappe.whitelist()
	def populate_deliveries(self):
		"""Fetch all un-settled deliveries for the transporter within the period."""
		if not self.transporter or not self.period_from or not self.period_to:
			frappe.throw(_("Please set Transporter, Period From and Period To first."))

		deliveries = frappe.get_all(
			"Aggregate Delivery",
			filters={
				"transporter": self.transporter,
				"dispatch_date": ["between", [self.period_from, self.period_to]],
				"status": ["in", ["Delivered", "Verified", "Dispatched"]],
				"docstatus": 1
			},
			fields=[
				"name", "dispatch_date", "pad_number", "truck",
				"loaded_volume", "delivered_volume", "shortage_volume",
				"transport_rate", "gross_truck_fee", "shortage_deduction", "net_truck_payment"
			],
			order_by="dispatch_date asc"
		)

		self.set("items", [])
		for d in deliveries:
			self.append("items", {
				"delivery": d.name,
				"dispatch_date": d.dispatch_date,
				"pad_number": d.pad_number,
				"truck": d.truck,
				"loaded_volume": d.loaded_volume,
				"delivered_volume": d.delivered_volume,
				"shortage_volume": d.shortage_volume,
				"transport_rate": d.transport_rate,
				"gross_truck_fee": d.gross_truck_fee,
				"shortage_deduction": d.shortage_deduction,
				"net_truck_payment": d.net_truck_payment
			})

		self.calculate_totals()
		return len(deliveries)
