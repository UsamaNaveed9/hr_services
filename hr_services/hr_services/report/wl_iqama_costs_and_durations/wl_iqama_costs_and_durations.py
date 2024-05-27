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
		{"label": _("Project ID"), "fieldname": "project_id", "fieldtype": "Link","options":"Project", "width": 140},
		{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 220},
		{"label": _("Iqama Duration"), "fieldname": "custom_iqama_duration", "fieldtype": "Data", "width": 150},
		{"label": _("Iqama Fees"), "fieldname": "iqama_fees", "fieldtype": "Currency", "width": 150},
		{"label": _("Working License Duration"), "fieldname": "custom_working_license", "fieldtype": "Data", "width": 190},
		{"label": _("Working License Fees"), "fieldname": "wl_fees", "fieldtype": "Currency", "width": 180}
	]
	
	return columns

def get_data(filters):
	# SQL query to get project details with concatenate insurance values
	query = """
		SELECT 
			p.name AS project_id,
			p.project_name AS project_name,
			p.custom_iqama_duration,
			p.custom_working_license
		FROM 
			`tabProject` p
		WHERE
			p.status = 'Open'
	"""
	
	# Check if 'company' filter is provided
	if filters.company:
		query += " AND p.company = %s "
	
	query += " GROUP BY p.name;"
	
	# Execute the query with filters
	results = frappe.db.sql(query, filters.company, as_dict=True)

	fees_doc = frappe.get_doc("Iqama and WL Fees",filters.company)

	for re in results:
		re["iqama_fees"] = (fees_doc.iqama_fee / 12) * int(re["custom_iqama_duration"])
		re["wl_fees"] = (fees_doc.working_license_fee / 12) * int(re["custom_working_license"])
		re["custom_iqama_duration"] += ' Months'
		re["custom_working_license"] += ' Months'

	return results