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
		{"label": _("Iqama No"), "fieldname": "iqama_no", "fieldtype": "Data", "width": 120},
		{"label": _("Gender"), "fieldname": "gender", "fieldtype": "Data", "width": 80},
		{"label": _("Health Insurance No"), "fieldname": "health_insurance_no", "fieldtype": "Data", "width": 160},
		{"label": _("Class"), "fieldname": "custom_class", "fieldtype": "Data", "width": 80},
		{"label": _("Has Family Insurance"), "fieldname": "family_insurance_status", "fieldtype": "Data", "width": 100},
		{"label": _("Family Members"), "fieldname": "custom_family_members", "fieldtype": "Data", "width": 130},
		{"label": _("Insurance Premium"), "fieldname": "custom_insurance_premium", "fieldtype": "Data", "width": 150},
		{"label": _("Insurance Invoice"), "fieldname": "custom_insurance_invoice", "fieldtype": "Data", "width": 200}
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
				gender,
				project AS project_id,
				project_name,
				health_insurance_no,
				custom_class,
				CASE
					WHEN custom_has_family_insurance = 1 THEN 'Yes'
					ELSE 'No'
				END AS family_insurance_status,
				custom_family_members,
				custom_insurance_premium,
				custom_insurance_invoice
			FROM 
				`tabEmployee`
			WHERE
				status = 'Active' %s
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