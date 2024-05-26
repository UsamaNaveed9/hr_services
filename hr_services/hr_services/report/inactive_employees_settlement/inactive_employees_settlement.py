# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from  frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"label": _("Project ID"), "fieldname": "project_id", "fieldtype": "Link","options":"Project", "width": 100},
		{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 120},
		{"label": _("Employee ID"), "fieldname": "employee_id", "fieldtype": "Link","options":"Employee", "width": 120},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 220},
		{"label": _("Iqama No"), "fieldname": "iqama_no", "fieldtype": "Data", "width": 110},
		{"label": _("Date of Joining"), "fieldname": "date_of_joining", "fieldtype": "Date", "width": 110},
		{"label": _("Leaving Date"), "fieldname": "relieving_date", "fieldtype": "Date", "width": 110},
		{"label": _("Health Insurance Cancelled"), "fieldname": "hi_cancelled", "fieldtype": "Data", "width": 200},
		{"label": _("Clearance Form Signed"), "fieldname": "cf_signed", "fieldtype": "Data", "width": 170},
		{"label": _("Nationality"), "fieldname": "nationality", "fieldtype": "Data", "width": 110},
		{"label": _("Gosi Removed"), "fieldname": "gosi_removed", "fieldtype": "Data", "width": 120},
		{"label": _("Left Type"), "fieldname": "left_type", "fieldtype": "Data", "width": 150}
	]
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	# SQL query to get project details with concatenate insurance values
	query = """
			SELECT 
				name AS employee_id,
				employee_name,
				iqama_national_id AS iqama_no,
				project AS project_id,
				project_name,
				date_of_joining,
				relieving_date,
				CASE
					WHEN custom_h_i_cancelled = 1 THEN 'Yes'
					ELSE 'No'
				END AS hi_cancelled,
				CASE
					WHEN custom_clearance_form_signed = 1 THEN 'Yes'
					ELSE 'No'
				END AS cf_signed,
				nationality,
				CASE
					WHEN custom_gosi_removed = 1 THEN 'Yes'
					ELSE 'No'
				END AS gosi_removed,
				custom_left_type AS left_type
			FROM 
				`tabEmployee`
			WHERE
				status = 'Inactive' %s
			GROUP BY 
				name;
		"""

	# Execute the query
	results = frappe.db.sql(query%(conditions), as_dict=True)

	return results

def get_conditions(filters):
	conditions = ""
	if filters.get("employee"):
		conditions += " and name = '%s'" % filters["employee"]
	

	if filters.get("project"):
		conditions += " and project = '%s'" % filters["project"]

	return conditions