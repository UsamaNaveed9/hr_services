# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from  frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data

def get_columns():
	columns = [
		{"label": _("Project ID"), "fieldname": "project_id", "fieldtype": "Link","options":"Project", "width": 200},
		{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 300},
		{"label": _("Class"), "fieldname": "class", "fieldtype": "Data", "width": 300}
	]
	
	return columns

def get_data():
	# SQL query to get project details with concatenate insurance values
	query = """
			SELECT 
				p.name AS project_id,
				p.project_name AS project_name,
				GROUP_CONCAT(c.insurance SEPARATOR ', ') AS class
			FROM 
				`tabProject` p
			LEFT JOIN 
				`tabHealth Insurances` c ON p.name = c.parent
			WHERE
				p.status = 'Open'	
			GROUP BY 
				p.name;
		"""

	# Execute the query
	results = frappe.db.sql(query, as_dict=True)

	return results
