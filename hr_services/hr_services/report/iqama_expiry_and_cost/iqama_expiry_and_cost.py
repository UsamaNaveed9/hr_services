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
			{"label": _("Iqama No"), "fieldname": "iqama_no", "fieldtype": "Data", "width": 110},
			{"label": _("Iqama Expiry Date"), "fieldname": "iqama_expiry_date", "fieldtype": "Date", "width": 120},
			{"label": _("Hijri Iqama Expiry Date"), "fieldname": "custom_iqama_expiry_date_in_hijri", "fieldtype": "Data", "width": 120},
			{"label": _("Iqama Duration"), "fieldname": "iqama_duration", "fieldtype": "Data", "width": 120},
			{"label": _("Iqama Cost"), "fieldname": "iqama_cost", "fieldtype": "Currency", "width": 110},
			{"label": _("WL Duration"), "fieldname": "wl_duration", "fieldtype": "Data", "width": 110},
			{"label": _("WL Cost"), "fieldname": "wl_cost", "fieldtype": "Currency", "width": 110},
			{"label": _("Total Cost(Iqama + WL)"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 120},
		]
	
	return columns


def get_employees(filters):
	conditions = get_conditions(filters)
	data = frappe.db.sql(
		"""select project as project_id, project_name,name as employee_id, employee_name, iqama_national_id as iqama_no, iqama_expiry_date, 
			custom_iqama_expiry_date_in_hijri, company
		  	from tabEmployee where status = 'Active' and nationality != 'Saudi Arabia' %s"""
		% conditions,
		as_dict=1,
	)

	for rec in data:
		if rec.project_id:
			project_doc = frappe.get_doc("Project",rec.project_id)
			iqama_duration = project_doc.custom_iqama_duration
			wl_duration = project_doc.custom_working_license
			fees_doc = frappe.get_doc("Iqama and WL Fees", rec.company)
			iqama_cost = (fees_doc.iqama_fee / 12) * int(iqama_duration)
			wl_cost = (fees_doc.working_license_fee / 12) * int(wl_duration)

			rec["iqama_duration"] = str(iqama_duration) + ' Months'
			rec["iqama_cost"] = iqama_cost
			rec["wl_duration"] = str(wl_duration) + ' Months'
			rec["wl_cost"] = wl_cost
			rec["total_cost"] = iqama_cost + wl_cost

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
		conditions += " and month(iqama_expiry_date) = '%s'" % month

	if filters.get("fiscal_year"):
		fiscal_year_start, fiscal_year_end = frappe.db.get_value("Fiscal Year",filters["fiscal_year"],["year_start_date","year_end_date"])
		conditions += " and iqama_expiry_date between '%s' and '%s'" % (fiscal_year_start, fiscal_year_end)
	if filters.get("company"):
		conditions += " and company = '%s'" % filters["company"].replace("'", "\\'")

	return conditions