# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint

def execute(filters=None):
	columns = get_columns()
	data = []

	row = {
		"client_name": "test",
		"shared_with_client": 0,
		"without_po": 0,
		"not_shared_yet": 0,
		"total": 0,
		"uploaded_on_client": 0
	}
	data.append(row)

	return columns, data

def get_columns():
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Client Name"),
			"fieldname": "client_name",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 220,
		},
		{
			"label": _("Shared with Client"),
			"fieldname": "shared_with_client",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"label": _("Without PO"),
			"fieldname": "without_po",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 160,
		},
		{
			"label": _("New Invoices Not Yet Shared"),
			"fieldname": "not_shared_yet",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 220,
		},
		{
			"label": _("Total as in Tracker"),
			"fieldname": "total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 160,
		},
		{
			"label": _("Uploaded on Client Portal"),
			"fieldname": "uploaded_on_client",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200,
		},
	]

	return columns
