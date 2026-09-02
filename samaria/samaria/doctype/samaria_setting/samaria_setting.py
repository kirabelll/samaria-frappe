"""
Samaria Setting Controller (Frappe v16)
"""
import frappe
from frappe import _
from frappe.model.document import Document


class SamariaSetting(Document):
	def validate(self):
		self.validate_sync_interval()
		self.validate_webhook()

	def validate_sync_interval(self):
		if self.sync_interval_mins and self.sync_interval_mins < 1:
			frappe.throw(_("Sync Interval must be at least 1 minute."))

	def validate_webhook(self):
		if self.webhook_url and not (
			self.webhook_url.startswith("http://") or self.webhook_url.startswith("https://")
		):
			frappe.throw(_("Webhook URL must start with http:// or https://"))
