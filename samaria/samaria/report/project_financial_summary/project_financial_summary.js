// Frappe Framework Version-16
frappe.query_reports["Project Financial Summary Report"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": __("Project / Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "division",
			"label": __("Division"),
			"fieldtype": "Select",
			"options": "\nAggregate\nCement\nMedical\nGeneral"
		},
		{
			"fieldname": "status",
			"label": __("Agreement Status"),
			"fieldtype": "Select",
			"options": "\nActive\nDraft\nExpired\nDeactivated\nCancelled"
		}
	]
};
