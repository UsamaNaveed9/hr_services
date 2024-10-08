# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):

	columns = get_columns()

	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Contract For PTs"),
			"fieldtype": "Link",
			"fieldname": "name",
			"options": "Contract For Part Timers",
			"width": 130,
		},
		{"label": _("Full Name"), "fieldtype": "data", "fieldname": "full_name", "width": 140},
		{
			"label": _("Status"),
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 90,
		},
		{
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 110,
		},
		{
			"label": _("Project Name"),
			"fieldtype": "Data",
			"fieldname": "project_name",
			"width": 100,
		},
		{
			"label": _("Nationality"),
			"fieldtype": "Data",
			"fieldname": "nationality",
			"width": 100,
		},
		{
			"label": _("Job Title"),
			"fieldtype": "Link",
			"fieldname": "job_title",
			"options": "Designation",
			"width": 130,
		},
		{"label": _("Department"), "fieldtype": "Link", "fieldname": "department", "options":"Department", "width": 130},
		{"label": _("Start Date"), "fieldtype": "Date", "fieldname": "start_date", "width": 100},
		{"label": _("Duration in Months"), "fieldtype": "Data", "fieldname": "duration_in_months", "width": 80},
		{"label": _("End Date"), "fieldtype": "Date", "fieldname": "end_date", "width": 100},
		{"label": _("Pricing Base On"), "fieldtype": "Data", "fieldname": "pricing_base_on", "width": 130},
		{"label": _("Rate"), "fieldtype": "Currency", "fieldname": "rate", "width": 130},
	]


def get_data(filters):
	if filters.status:
		contracts = frappe.get_all(
			"Contract For Part Timers",
			filters=[["status","=",filters.status]],
			fields=["name", "full_name", "status","project", "nationality", "job_title","project_name","department","start_date",
					"duration_in_months","end_date","pricing_base_on","rate"],
			order_by="creation desc"	  
		)
	else:
		contracts = frappe.get_all(
			"Contract For Part Timers",
			fields=["name", "full_name", "status","project", "nationality", "job_title","project_name","department","start_date",
					"duration_in_months","end_date","pricing_base_on","rate"],
			order_by="creation desc"	  
		)

	return contracts