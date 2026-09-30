app_name = "samaria"
app_title = "Samaria ERP"
app_publisher = "Samaria ERP Team"
app_description = "Specialized Frappe v15 app for Aggregate, Cement, Medical, and Transporter operations"
app_email = "info@samariaerp.com"
app_license = "mit"
required_apps = []

# App includes
# app_include_css = "/assets/samaria/css/samaria.bundle.css"
# app_include_js = "/assets/samaria/js/samaria.bundle.js"

# Home page
home_page = "index"

# Document Events
doc_events = {
	"Aggregate Delivery": {
		"validate": "samaria.samaria.doctype.aggregate_delivery.aggregate_delivery.AggregateDelivery.validate",
		"on_submit": "samaria.samaria.doctype.aggregate_delivery.aggregate_delivery.AggregateDelivery.on_submit"
	},
	"Aggregate Settlement": {
		"validate": "samaria.samaria.doctype.aggregate_settlement.aggregate_settlement.AggregateSettlement.validate",
		"on_submit": "samaria.samaria.doctype.aggregate_settlement.aggregate_settlement.AggregateSettlement.on_submit",
		"on_cancel": "samaria.samaria.doctype.aggregate_settlement.aggregate_settlement.AggregateSettlement.on_cancel"
	},
	"Cement Purchase": {
		"validate": "samaria.samaria.doctype.cement_purchase.cement_purchase.CementPurchase.validate"
	},
	"Cement Lifting": {
		"validate": "samaria.samaria.doctype.cement_lifting.cement_lifting.CementLifting.validate",
		"on_submit": "samaria.samaria.doctype.cement_lifting.cement_lifting.CementLifting.on_submit",
		"on_cancel": "samaria.samaria.doctype.cement_lifting.cement_lifting.CementLifting.on_cancel"
	},
	"Cement Coupon": {
		"validate": "samaria.samaria.doctype.cement_coupon.cement_coupon.CementCoupon.validate"
	},
	"Cement Penalty": {
		"validate": "samaria.samaria.doctype.cement_penalty.cement_penalty.CementPenalty.validate"
	},
	"Medical Batch": {
		"validate": "samaria.samaria.doctype.medical_batch.medical_batch.MedicalBatch.validate"
	},
	"Medical Pricing": {
		"validate": "samaria.samaria.doctype.medical_pricing.medical_pricing.MedicalPricing.validate"
	},
	"Medical Request": {
		"validate": "samaria.samaria.doctype.medical_request.medical_request.MedicalRequest.validate"
	},
	"Medical Store Issue": {
		"validate": "samaria.samaria.doctype.medical_store_issue.medical_store_issue.MedicalStoreIssue.validate",
		"on_submit": "samaria.samaria.doctype.medical_store_issue.medical_store_issue.MedicalStoreIssue.on_submit",
		"on_cancel": "samaria.samaria.doctype.medical_store_issue.medical_store_issue.MedicalStoreIssue.on_cancel"
	},
	"Medical Batch Adjustment": {
		"on_submit": "samaria.samaria.doctype.medical_batch_adjustment.medical_batch_adjustment.MedicalBatchAdjustment.on_submit",
		"on_cancel": "samaria.samaria.doctype.medical_batch_adjustment.medical_batch_adjustment.MedicalBatchAdjustment.on_cancel"
	},
	"Truck": {
		"validate": "samaria.samaria.doctype.truck.truck.Truck.validate"
	},
	"Transporter Recovery": {
		"validate": "samaria.samaria.doctype.transporter_recovery.transporter_recovery.TransporterRecovery.validate"
	},
	"Sales Agreement": {
		"validate": "samaria.samaria.doctype.sales_agreement.sales_agreement.SalesAgreement.validate"
	},
	"Supplier Agreement": {
		"validate": "samaria.samaria.doctype.supplier_agreement.supplier_agreement.SupplierAgreement.validate"
	}
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"samaria.tasks.cron.daily"
	],
	"hourly": [
		"samaria.tasks.cron.hourly"
	]
}

# Fixtures - install custom roles
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
