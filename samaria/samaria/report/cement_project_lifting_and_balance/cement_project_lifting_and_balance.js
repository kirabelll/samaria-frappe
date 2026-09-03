// Frappe Framework Version-16
frappe.query_reports["Cement Project Lifting and Balance Report"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": __("Project / Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "factory",
			"label": __("Cement Factory"),
			"fieldtype": "Link",
			"options": "Cement Factory"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nLifted\nDelivered\nVerified\nCancelled"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
