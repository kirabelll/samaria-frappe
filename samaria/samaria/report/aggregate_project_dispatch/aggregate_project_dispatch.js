// Frappe Framework Version-16
frappe.query_reports["Aggregate Project Dispatch Report"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": __("Project / Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "supplier",
			"label": __("Quarry / Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "transporter",
			"label": __("Transporter"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDispatched\nDelivered\nVerified\nSettled\nCancelled"
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
