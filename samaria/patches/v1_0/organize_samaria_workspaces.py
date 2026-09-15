import frappe


def execute():
	"""
	Organizes all Samaria division workspaces cleanly under the primary Samaria Operations workspace.
	"""
	# Ensure primary Samaria workspace is top-level
	if frappe.db.exists("Workspace", "Samaria"):
		frappe.db.set_value("Workspace", "Samaria", {
			"parent_page": "",
			"label": "Samaria Operations",
			"title": "Samaria Operations",
			"sequence_id": 1.0,
			"public": 1,
			"is_hidden": 0
		}, update_modified=False)

	# Group all division workspaces under the 'Samaria' root page
	sub_workspaces = [
		("Aggregate Operations", 2.0),
		("Cement Operations", 3.0),
		("Medical Division", 4.0),
		("Agreements & Commercial", 5.0),
		("Samaria Project Reports", 6.0)
	]

	for ws_name, seq in sub_workspaces:
		if frappe.db.exists("Workspace", ws_name):
			frappe.db.set_value("Workspace", ws_name, {
				"parent_page": "Samaria",
				"sequence_id": seq,
				"public": 1,
				"is_hidden": 0
			}, update_modified=False)

	frappe.clear_cache()
