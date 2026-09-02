"""
Samaria Scheduled Background Tasks
"""
import frappe


def hourly():
	"""Runs hourly scheduled background routines."""
	frappe.logger("samaria").debug("Executing Samaria hourly cron task")


def daily():
	"""Runs daily scheduled background routines."""
	frappe.logger("samaria").debug("Executing Samaria daily cron task")
