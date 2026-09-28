# Copyright (c) 2026, Samaria and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestSamariaSetting(FrappeTestCase):
	def test_setting_validation(self):
		setting = frappe.get_single("Samaria Setting")
		setting.enabled = 1
		setting.sync_interval_mins = 30
		setting.webhook_url = "https://api.samaria.local/webhook"
		setting.save()

		self.assertEqual(setting.sync_interval_mins, 30)
