import frappe
from frappe.model.document import Document

class AggregateSettlement(Document):
	def validate(self):
		self.calculate_settlement()

	def calculate_settlement(self):
		gross = float(self.total_gross_fee or 0)
		shortage = float(self.total_shortage_deduction or 0)
		net = max(0.0, gross - shortage)
		self.total_net_payment = net

		comm_rate = float(self.commission_rate or 0)
		comm_amt = (comm_rate / 100.0) * net
		self.commission_amount = comm_amt
		self.final_payable = max(0.0, net - comm_amt)
