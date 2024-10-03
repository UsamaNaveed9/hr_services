# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class ContractForPartTimers(Document):
	def validate(self):
		self.validate_dates()
		self.update_contract_status()
		self.set_full_name()

	def validate_dates(self):
		if self.end_date and self.end_date < self.start_date:
			frappe.throw(_("End Date cannot be before Start Date."))

	def update_contract_status(self):
		if self.is_signed:
			self.status = get_status(self.start_date, self.end_date)
		else:
			self.status = "Unsigned"

	def set_full_name(self):
		self.full_name = " ".join(
			filter(lambda x: x, [self.first_name, self.last_name])
		)		

def get_status(start_date, end_date):
	"""
	Get a Contract's status based on the start, current and end dates

	Args:
			start_date (str): The start date of the contract
			end_date (str): The end date of the contract

	Returns:
			str: 'Active' if within range, otherwise 'Inactive'
	"""

	if not end_date:
		return "Active"

	start_date = getdate(start_date)
	end_date = getdate(end_date)
	now_date = getdate(nowdate())

	return "Active" if start_date <= now_date <= end_date else "Inactive"

def update_status_for_contracts():
	"""
	Run the daily hook to update the statuses for all signed
	"""

	part_timers_contracts = frappe.get_all(
		"Contract For Part Timers",
		filters={"is_signed": 1},
		fields=["name", "start_date", "end_date"],
	)

	for contract in part_timers_contracts:
		status = get_status(contract.get("start_date"), contract.get("end_date"))

		frappe.db.set_value("Contract For Part Timers", contract.get("name"), "status", status)