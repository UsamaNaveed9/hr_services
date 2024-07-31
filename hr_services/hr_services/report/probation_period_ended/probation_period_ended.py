# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_employees(filters)

	return columns, data


def get_columns():
	columns = [
			{"label": _("Project ID"), "fieldname": "project_id", "fieldtype": "Link","options":"Project", "width": 100},
			{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 120},
			{"label": _("Employee ID"), "fieldname": "employee_id", "fieldtype": "Link","options":"Employee", "width": 120},
			{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
			{"label": _("Date of Joining"), "fieldname": "date_of_joining", "fieldtype": "Date", "width": 200},
			{"label": _("Probation Period(Days)"), "fieldname": "probation_period", "fieldtype": "Data", "width": 200},
			{"label": _("Probation End Date"), "fieldname": "probation_end_date", "fieldtype": "Date", "width": 200},
		]
	
	return columns


def get_employees(filters):
	conditions = get_conditions(filters)
	data = frappe.db.sql(
		"""select project as project_id, project_name,name as employee_id, employee_name, date_of_joining, custom_probation_period as probation_period, 
			custom_probation_end_date as probation_end_date
		  	from tabEmployee where status = 'Active' %s"""
		% conditions,
		as_dict=1,
	)

	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		].index(filters["month"]) + 1
		conditions += " and month(custom_probation_end_date) = '%s'" % month

	if filters.get("fiscal_year"):
		fiscal_year_start, fiscal_year_end = frappe.db.get_value("Fiscal Year",filters["fiscal_year"],["year_start_date","year_end_date"])
		conditions += " and custom_probation_end_date between '%s' and '%s'" % (fiscal_year_start, fiscal_year_end)
	if filters.get("company"):
		conditions += " and company = '%s'" % filters["company"].replace("'", "\\'")

	return conditions