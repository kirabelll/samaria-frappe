// Frappe Framework Version-16
frappe.query_reports["Medical Project Inventory Report"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Medical Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nAvailable\nReserved\nQuarantine\nExpired\nDamaged\nRecalled"
		},
		{
			"fieldname": "expiry_status",
			"label": __("Expiry Alert"),
			"fieldtype": "Select",
			"options": "\nNear Expiry (<90 Days)\nExpired\nSafe"
		}
	]
};
