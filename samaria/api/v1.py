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
