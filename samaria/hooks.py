app_name = "samaria"
app_title = "Samaria ERP"
app_publisher = "Samaria ERP Team"
app_description = "Specialized Frappe v15 app for Aggregate, Cement, Medical, and Transporter operations"
app_email = "info@samariaerp.com"
app_license = "mit"
required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/samaria/css/samaria.bundle.css"
# app_include_js = "/assets/samaria/js/samaria.bundle.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "index"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Aggregate Delivery": {
		"validate": "samaria.aggregate.doctype.aggregate_delivery.aggregate_delivery.calculate_totals",
		"on_submit": "samaria.aggregate.doctype.aggregate_delivery.aggregate_delivery.on_submit_handler"
	},
	"Cement Lifting": {
		"validate": "samaria.cement.doctype.cement_lifting.cement_lifting.calculate_lifting",
		"on_submit": "samaria.cement.doctype.cement_lifting.cement_lifting.on_submit_handler",
		"on_cancel": "samaria.cement.doctype.cement_lifting.cement_lifting.on_cancel_handler"
	},
	"Cement Coupon": {
		"validate": "samaria.cement.doctype.cement_coupon.cement_coupon.validate_coupon"
	},
	"Medical Store Issue": {
		"validate": "samaria.medical.doctype.medical_store_issue.medical_store_issue.validate_batches",
		"on_submit": "samaria.medical.doctype.medical_store_issue.medical_store_issue.on_submit_handler"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"samaria.tasks.cron.daily"
	],
	"hourly": [
		"samaria.tasks.cron.hourly"
	]
}

# Fixtures
# --------
fixtures = [
	{
		"dt": "Role",
		"filters": [
			["name", "in", [
				"Aggregate Manager",
				"Cement Manager",
				"Medical Pharmacist",
				"Medical Druggist",
				"Transporter Coordinator",
				"Weighbridge Operator"
			]]
		]
	}
]
