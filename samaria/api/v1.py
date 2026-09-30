"""
Samaria v1 REST API
Unified REST wrapper exposing all division endpoints with consistent response format
"""

import frappe
from frappe import _
from typing import Dict, Any, List, Optional
from datetime import datetime

from samaria.api import aggregate, cement, medical, transporter


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def api_response(success: bool = True, data: Any = None, message: str = None, error: str = None) -> Dict:
    """Standardized API response format"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    if error:
        response["error"] = error
    return response


# ============================================================================
# GENERAL ENDPOINTS
# ============================================================================

@frappe.whitelist(allow_guest=True)
def ping() -> Dict:
    """Health check endpoint"""
    return api_response(data={"status": "ok", "app": "Samaria", "version": "1.0.0"})


@frappe.whitelist()
def get_app_info() -> Dict:
    """Get application metadata"""
    return api_response(data={
        "app_name": "Samaria",
        "version": "1.0.0",
        "frappe_version": frappe.__version__,
        "divisions": ["aggregate", "cement", "medical", "transporter"],
        "user": frappe.session.user,
        "company": frappe.defaults.get_user_default("Company"),
    })


# ============================================================================
# AGGREGATE DIVISION
# ============================================================================

@frappe.whitelist()
def get_unsettled_deliveries(customer: str = None, project: str = None, transporter: str = None) -> Dict:
    """Get all unsettled aggregate deliveries"""
    try:
        data = aggregate.get_unsettled_deliveries(customer, project, transporter)
        return api_response(data=data, message=f"Found {len(data)} unsettled deliveries")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_unsettled_deliveries")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_aggregate_analytics(customer: str = None, from_date: str = None, to_date: str = None) -> Dict:
    """Get aggregate division analytics"""
    try:
        data = aggregate.get_aggregate_analytics(customer, from_date, to_date)
        return api_response(data=data)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_aggregate_analytics")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_deliveries_by_transporter(transporter: str, from_date: str = None, to_date: str = None) -> Dict:
    """Get aggregate deliveries by transporter"""
    try:
        data = aggregate.get_deliveries_by_transporter(transporter, from_date, to_date)
        return api_response(data=data, message=f"Found {len(data)} deliveries")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_deliveries_by_transporter")
        return api_response(success=False, error=str(e))


# ============================================================================
# CEMENT DIVISION
# ============================================================================

@frappe.whitelist()
def get_factory_balances(factory: str = None, show_exhausted: bool = False) -> Dict:
    """Get cement factory balances"""
    try:
        data = cement.get_factory_balances(factory, show_exhausted)
        return api_response(data=data, message=f"Found {len(data)} balance records")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_factory_balances")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_cement_analytics(factory: str = None, from_date: str = None, to_date: str = None) -> Dict:
    """Get cement division analytics"""
    try:
        data = cement.get_cement_analytics(factory, from_date, to_date)
        return api_response(data=data)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_cement_analytics")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_liftings_by_factory(factory: str, from_date: str = None, to_date: str = None, customer: str = None) -> Dict:
    """Get cement liftings by factory"""
    try:
        data = cement.get_liftings_by_factory(factory, from_date, to_date, customer)
        return api_response(data=data, message=f"Found {len(data)} liftings")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_liftings_by_factory")
        return api_response(success=False, error=str(e))


# ============================================================================
# MEDICAL DIVISION
# ============================================================================

@frappe.whitelist()
def get_fefo_batches(item_code: str = None, min_qty: float = None) -> Dict:
    """Get available medical batches in FEFO order"""
    try:
        data = medical.get_fefo_batches(item_code, min_qty)
        return api_response(data=data, message=f"Found {len(data)} available batches")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_fefo_batches")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def create_store_issue_from_request(medical_request: str) -> Dict:
    """Create Medical Store Issue from Medical Request with FEFO allocation"""
    try:
        store_issue_name = medical.create_store_issue_from_request(medical_request)
        return api_response(
            data={"store_issue": store_issue_name},
            message=f"Store Issue {store_issue_name} created successfully"
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: create_store_issue_from_request")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_expiring_batches(days_threshold: int = 90) -> Dict:
    """Get medical batches expiring within threshold"""
    try:
        data = medical.get_expiring_batches_report(days_threshold)
        return api_response(data=data, message=f"Found {len(data)} batches expiring soon")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_expiring_batches")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_medical_inventory_summary(item_code: str = None) -> Dict:
    """Get medical inventory summary by status"""
    try:
        data = medical.get_medical_inventory_summary(item_code)
        return api_response(data=data)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_medical_inventory_summary")
        return api_response(success=False, error=str(e))


# ============================================================================
# TRANSPORTER DIVISION
# ============================================================================

@frappe.whitelist()
def get_active_transport_rate(transporter: str, item_type: str, from_location: str = None, to_location: str = None) -> Dict:
    """Get active transport rate from agreement"""
    try:
        rate = transporter.get_active_rate(transporter, item_type, from_location, to_location)
        if rate:
            return api_response(data={"rate": rate}, message="Active rate found")
        else:
            return api_response(success=False, error="No active agreement found for the given criteria")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_active_transport_rate")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_transporter_recovery_balance(transporter: str = None) -> Dict:
    """Get transporter recovery outstanding balance"""
    try:
        data = transporter.get_transporter_recovery_balance(transporter)
        return api_response(data=data, message=f"Found {len(data)} recovery records")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_transporter_recovery_balance")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_active_trucks(transporter: str = None) -> Dict:
    """Get all active trucks"""
    try:
        data = transporter.get_active_trucks(transporter)
        return api_response(data=data, message=f"Found {len(data)} active trucks")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_active_trucks")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_transporter_summary(transporter: str = None, from_date: str = None, to_date: str = None) -> Dict:
    """Get transporter performance summary"""
    try:
        data = transporter.get_transporter_summary(transporter, from_date, to_date)
        return api_response(data=data)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_transporter_summary")
        return api_response(success=False, error=str(e))


# ============================================================================
# CROSS-DIVISION QUERIES
# ============================================================================

@frappe.whitelist()
def get_customer_overview(customer: str, from_date: str = None, to_date: str = None) -> Dict:
    """Get comprehensive customer overview across all divisions"""
    try:
        overview = {
            "customer": customer,
            "aggregate": aggregate.get_aggregate_analytics(customer, from_date, to_date),
            "cement": cement.get_cement_analytics(None, from_date, to_date),  # Filter by customer in query
            "medical": medical.get_medical_inventory_summary(),  # Filter by customer in subsequent call
        }
        return api_response(data=overview)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_customer_overview")
        return api_response(success=False, error=str(e))


@frappe.whitelist()
def get_project_summary(project: str) -> Dict:
    """Get project summary across aggregate and cement divisions"""
    try:
        # Aggregate data
        agg_deliveries = frappe.db.sql("""
            SELECT COUNT(*) as count, SUM(quantity) as total_qty, SUM(amount) as total_amount
            FROM `tabAggregate Delivery`
            WHERE project = %s AND docstatus = 1
        """, project, as_dict=True)[0]
        
        # Cement data
        cement_liftings = frappe.db.sql("""
            SELECT COUNT(*) as count, SUM(factory_weighbridge_qty) as total_qty, SUM(customer_amount) as total_amount
            FROM `tabCement Lifting`
            WHERE project = %s AND docstatus = 1
        """, project, as_dict=True)[0]
        
        data = {
            "project": project,
            "aggregate": agg_deliveries,
            "cement": cement_liftings,
        }
        return api_response(data=data)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API: get_project_summary")
        return api_response(success=False, error=str(e))
