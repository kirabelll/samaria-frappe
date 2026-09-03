"""
Samaria API Module
"""
import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def ping():
	"""Simple ping endpoint to verify Frappe v16 App API availability."""
	return {
		"status": "success",
		"message": _("Samaria Frappe v16 App is running"),
		"version": "16.0.0-compat",
		"user": frappe.session.user
	}


@frappe.whitelist()
def get_app_info():
	"""Returns metadata and runtime configuration."""
	return {
		"app_name": "samaria",
		"app_title": "Samaria",
		"version": "0.0.1",
		"modules": ["Samaria"]
	}


@frappe.whitelist()
def get_dashboard_data(customer=None, from_date=None, to_date=None):
	"""Proxy to samaria executive dashboard metrics."""
	from samaria.samaria.page.samaria_dashboard.samaria_dashboard import get_dashboard_data as _get_data
	return _get_data(customer=customer, from_date=from_date, to_date=to_date)
