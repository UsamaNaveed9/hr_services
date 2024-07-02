# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from  frappe import _
from datetime import datetime, date


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"label": _("Job Offer"), "fieldname": "job_offer", "fieldtype": "Link","options":"Job Offer", "width": 160},
		{"label": _("Applicant Name"), "fieldname": "applicant_name", "fieldtype": "Data", "width": 180},
		{"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 180},
		{"label": _("Project ID"), "fieldname": "project_id", "fieldtype": "Link","options":"Project", "width": 100},
		{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 180},
		{"label": _("Offer Date"), "fieldname": "offer_date", "fieldtype": "Date", "width": 130},
		{"label": _("Valid Days"), "fieldname": "valid_days", "fieldtype": "Int", "width": 130},
		{"label": _("Passed Days"), "fieldname": "passed_days", "fieldtype": "Int", "width": 130},
	]
	
	return columns

def get_data(filters):
	# SQL query to get project details with concatenate insurance values
	query = """
		SELECT 
			j.name AS job_offer,
			j.applicant_name,
			j.designation,
			j.custom_project AS project_id,
			j.custom_project_name AS project_name,
			j.offer_date
		FROM 
			`tabJob Offer` j
		WHERE
			j.status = 'Awaiting Response'
	"""
	
	# Check if 'company' filter is provided
	if filters.company:
		query += " AND j.company = %s "
	
	query += " GROUP BY j.name;"
	
	# Execute the query with filters
	results = frappe.db.sql(query, filters.company, as_dict=True)

	for re in results:
		re["valid_days"] = frappe.get_value("Project",re.project_id,"custom_jo_valid_days")

		# Get today's date
		today_date = date.today()

		# Calculate the difference in days
		days_passed = (today_date - re.offer_date).days

		re["passed_days"] = days_passed


	return results