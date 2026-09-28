"""
Samaria API Module
Exposes RESTful whitelisted endpoints for Samaria ERP v15 Integration
"""
import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days


@frappe.whitelist(allow_guest=False)
def ping():
	"""Simple ping endpoint to verify Frappe v15 App API availability."""
	return {
		"status": "success",
		"message": _("Samaria Frappe v15 App is running"),
		"version": "15.0.0",
		"user": frappe.session.user
	}


@frappe.whitelist()
def get_app_info():
	"""Returns metadata and runtime configuration."""
	return {
		"app_name": "samaria",
		"app_title": "Samaria",
		"version": "1.0.0",
		"divisions": ["Aggregate", "Cement", "Medical", "Commercial"]
	}


@frappe.whitelist()
def get_dashboard_data(customer=None, from_date=None, to_date=None):
	"""Proxy to samaria executive dashboard metrics."""
	from samaria.samaria.page.samaria_dashboard.samaria_dashboard import get_dashboard_data as _get_data
	return _get_data(customer=customer, from_date=from_date, to_date=to_date)


# -------------------------------------------------------------
# AGGREGATE API ENDPOINTS
# -------------------------------------------------------------
@frappe.whitelist()
def get_aggregate_deliveries(status=None, customer=None, transporter=None, from_date=None, to_date=None, limit=50):
	"""Query aggregate delivery dispatches with pricing breakdowns."""
	filters = {}
	if status:
		filters["status"] = status
	if customer:
		filters["customer"] = customer
	if transporter:
		filters["transporter"] = transporter
	if from_date and to_date:
		filters["dispatch_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["dispatch_date"] = [">=", from_date]
	elif to_date:
		filters["dispatch_date"] = ["<=", to_date]

	return frappe.get_all(
		"Aggregate Delivery",
		filters=filters,
		fields=[
			"name", "naming_series", "customer", "customer_name",
			"supplier", "supplier_name", "transporter", "transporter_name",
			"truck", "truck_capacity", "item", "item_name",
			"pad_number", "dispatch_date", "delivery_date", "status",
			"loaded_volume", "delivered_volume", "shortage_volume", "billable_volume",
			"transport_rate", "aggregate_value", "customer_price",
			"gross_truck_fee", "shortage_deduction", "net_truck_payment",
			"customer_receivable", "supplier_payable", "net_profit_amount"
		],
		order_by="dispatch_date desc, creation desc",
		limit=flt(limit) or 50
	)


# -------------------------------------------------------------
# CEMENT API ENDPOINTS
# -------------------------------------------------------------
@frappe.whitelist()
def get_cement_liftings(status=None, customer=None, factory=None, from_date=None, to_date=None, limit=50):
	"""Query cement lifting records with weighbridge & shortage details."""
	filters = {}
	if status:
		filters["status"] = status
	if customer:
		filters["customer"] = customer
	if factory:
		filters["factory"] = factory
	if from_date and to_date:
		filters["lifting_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["lifting_date"] = [">=", from_date]
	elif to_date:
		filters["lifting_date"] = ["<=", to_date]

	return frappe.get_all(
		"Cement Lifting",
		filters=filters,
		fields=[
			"name", "purchase", "factory", "customer", "customer_name",
			"truck", "self_transport", "self_plate_no", "self_driver_name",
			"coupon", "delivery_note_no", "pod_number", "pad_number",
			"lifting_date", "status",
			"factory_weighbridge_ref", "factory_weight", "buyer_weighbridge_qty",
			"shortage_qty", "shortage_penalty"
		],
		order_by="lifting_date desc, creation desc",
		limit=flt(limit) or 50
	)


@frappe.whitelist()
def get_cement_purchases(status=None, factory=None):
	"""Query active cement purchase contracts and remaining balances."""
	filters = {}
	if status:
		filters["status"] = status
	if factory:
		filters["factory"] = factory

	return frappe.get_all(
		"Cement Purchase",
		filters=filters,
		fields=[
			"name", "factory", "cement_type", "quantity_tons",
			"unit_price", "total_amount", "vat_rate", "vat_amount",
			"paid_amount", "balance_remaining", "status", "payment_status", "purchase_date"
		],
		order_by="purchase_date desc"
	)


# -------------------------------------------------------------
# MEDICAL API ENDPOINTS
# -------------------------------------------------------------
@frappe.whitelist()
def get_medical_batches(status=None, item_code=None, warehouse=None):
	"""Query medical batches with FEFO sorting and expiry info."""
	filters = {}
	if status:
		filters["status"] = status
	if item_code:
		filters["item_code"] = item_code
	if warehouse:
		filters["warehouse"] = warehouse

	return frappe.get_all(
		"Medical Batch",
		filters=filters,
		fields=[
			"name", "item_code", "item_name", "batch_no",
			"status", "expiry_date", "days_to_expiry",
			"quantity", "cost_price", "warehouse", "supplier", "received_date"
		],
		order_by="expiry_date asc"
	)


@frappe.whitelist()
def get_medical_requests(status=None, customer=None):
	"""Query medical customer requests."""
	filters = {}
	if status:
		filters["status"] = status
	if customer:
		filters["customer"] = customer

	requests = frappe.get_all(
		"Medical Request",
		filters=filters,
		fields=[
			"name", "customer", "customer_name", "license_no", "license_expiry",
			"status", "priority", "request_date", "total_items_count", "total_amount"
		],
		order_by="request_date desc, creation desc"
	)

	for req in requests:
		req["items"] = frappe.get_all(
			"Medical Request Item",
			filters={"parent": req["name"]},
			fields=["item_code", "item_name", "qty", "unit", "unit_price", "total_amount", "batch_preference", "notes"]
		)

	return requests
