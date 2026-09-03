"""
Samaria ERP - Website Home Page Context Provider
Frappe Framework Version-16
"""
import frappe
from frappe import _


def get_context(context):
	context.no_cache = 1
	context.title = _("Samaria ERP - Unified Enterprise Operations")
	context.meta_description = _("Enterprise Operations Management for Aggregate, Cement, Medical Divisions and Transporter Logistics.")

	# Fetch live operational indicators safely with fallbacks
	context.metrics = get_live_metrics()
	context.divisions = get_division_summaries()
	context.active_projects = get_active_projects_summary()

	return context


def get_live_metrics():
	"""Gathers aggregate statistics across the divisions for the hero section."""
	metrics = {
		"aggregate_dispatches": 0,
		"aggregate_volume": 0.0,
		"cement_liftings": 0,
		"cement_tonnage": 0.0,
		"medical_batches": 0,
		"active_agreements": 0
	}

	try:
		if frappe.db.table_exists("Aggregate Delivery"):
			metrics["aggregate_dispatches"] = frappe.db.count("Aggregate Delivery")
			vol_data = frappe.db.sql("""
				SELECT COALESCE(SUM(delivered_volume), 0) as total_vol
				FROM `tabAggregate Delivery`
				WHERE docstatus < 2
			""", as_dict=True)
			if vol_data:
				metrics["aggregate_volume"] = round(float(vol_data[0].get("total_vol", 0)), 1)
	except Exception:
		pass

	try:
		if frappe.db.table_exists("Cement Lifting"):
			metrics["cement_liftings"] = frappe.db.count("Cement Lifting")
			cement_data = frappe.db.sql("""
				SELECT COALESCE(SUM(buyer_weighbridge_qty), 0) as total_tons
				FROM `tabCement Lifting`
				WHERE docstatus < 2
			""", as_dict=True)
			if cement_data:
				metrics["cement_tonnage"] = round(float(cement_data[0].get("total_tons", 0)), 1)
	except Exception:
		pass

	try:
		if frappe.db.table_exists("Medical Batch"):
			metrics["medical_batches"] = frappe.db.count("Medical Batch", {"is_quarantined": 0})
	except Exception:
		pass

	try:
		if frappe.db.table_exists("Sales Agreement"):
			metrics["active_agreements"] = frappe.db.count("Sales Agreement", {"status": "Active"})
	except Exception:
		pass

	return metrics


def get_division_summaries():
	"""Summaries of core operational divisions for interactive cards."""
	return [
		{
			"id": "aggregate",
			"name": _("Aggregate & Quarry"),
			"badge": _("Mining & Logistics"),
			"icon": "truck",
			"color": "orange",
			"description": _("Stone crushing, quarry extraction, weighbridge tracking, transport fleet settlements, and shortage control."),
			"doctypes": ["Aggregate Delivery", "Transporter Agreement", "Truck", "Aggregate Settlement"],
			"desk_link": "/app/aggregate-operations"
		},
		{
			"id": "cement",
			"name": _("Cement Supply Chain"),
			"badge": _("Factory Distribution"),
			"icon": "box",
			"color": "emerald",
			"description": _("Direct-from-plant bulk cement allocation, physical coupon validation, driver lifting tickets, and weighbridge variances."),
			"doctypes": ["Cement Purchase", "Cement Lifting", "Cement Coupon", "Cement Factory"],
			"desk_link": "/app/cement-operations"
		},
		{
			"id": "medical",
			"name": _("Medical & Healthcare"),
			"badge": _("Pharma & Laboratory"),
			"icon": "heart-pulse",
			"color": "rose",
			"description": _("Pharmaceutical batch tracking, FEFO release logic, expiry alerts, cold-chain quarantine compliance, and health center quotes."),
			"doctypes": ["Medical Batch", "Medical Request", "Medical Pricing", "Medical Batch Adjustment"],
			"desk_link": "/app/medical-division"
		},
		{
			"id": "agreements",
			"name": _("Commercial Agreements"),
			"badge": _("Finance & Compliance"),
			"icon": "file-text",
			"color": "violet",
			"description": _("B2B sales agreements, supplier framework contracts, transporter rate matrices with VAT inclusion/exclusion enforcement."),
			"doctypes": ["Sales Agreement", "Supplier Agreement", "Transport Association", "Samaria Setting"],
			"desk_link": "/app/agreements-and-commercial"
		}
	]


def get_active_projects_summary():
	"""Lists top active projects or customer offloading sites."""
	projects = []
	try:
		if frappe.db.table_exists("Sales Agreement"):
			agreements = frappe.get_all(
				"Sales Agreement",
				filters={"status": "Active"},
				fields=["name", "customer", "customer_name", "division", "offloading_site", "total_amount"],
				limit=5,
				order_by="modified desc"
			)
			for agr in agreements:
				projects.append({
					"title": agr.offloading_site or agr.customer_name or agr.customer,
					"customer": agr.customer_name or agr.customer,
					"division": agr.division or "Commercial",
					"agreement": agr.name,
					"budget": agr.total_amount or 0
				})
	except Exception:
		pass

	return projects
