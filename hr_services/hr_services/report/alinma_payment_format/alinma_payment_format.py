# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")

def execute(filters=None):
	if not filters:
		filters = {}

	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))

	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []
	
	columns = get_columns()

	data = []
	for ss in salary_slips:
		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
		}

		emp_doc = frappe.get_doc("Employee",ss.employee)
		basic_housing = flt(emp_doc.basic_salary) + flt(emp_doc.housing_allowance)
		
		row.update(
			{
				"employee_name": emp_doc.custom_emp_name_in_bank,
				"account": emp_doc.iban or emp_doc.bank_ac_no, 
				"bank": emp_doc.bank_name,
				"payment_method": "BANK ACCOUNT" if emp_doc.bank_name == "INMA" else "SARIE",
				"legal_no": emp_doc.iqama_national_id,
				"basic": round((flt(emp_doc.basic_salary) * flt(ss.exchange_rate)), 2),
				"housing": round((flt(emp_doc.housing_allowance) * flt(ss.exchange_rate)), 2),
				"other_earnings": round(((flt(ss.gross_pay) - flt(basic_housing)) * flt(ss.exchange_rate)), 2),
				"deductions": round(((flt(ss.total_deduction) + flt(ss.total_loan_repayment)) * flt(ss.exchange_rate)), 2),
			}
		)

		if currency == company_currency:
			row.update(
				{
					"amount": round((flt(ss.net_pay) * flt(ss.exchange_rate)), 2),
				}
			)

		data.append(row)

	return columns, data

def get_columns():
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 170,
		},
		{
			"label": _("Employee No"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 130,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Account No"),
			"fieldname": "account",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Bank"),
			"fieldname": "bank",
			"fieldtype": "Data",
			"width": 90,
		},
		{
			"label": _("Payment Method"),
			"fieldname": "payment_method",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Legal No"),
			"fieldname": "legal_no",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Employee Basic Wage"),
			"fieldname": "basic",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Housing Allowance"),
			"fieldname": "housing",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Other Earnings"),
			"fieldname": "other_earnings",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Deductions"),
			"fieldname": "deductions",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
	]
	
	return columns


def get_salary_slips(filters, company_currency):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	conditions = []

	if filters.get("docstatus"):
		val_status = doc_status[filters.get("docstatus")]
		conditions.append(f"docstatus = {val_status}")

	if filters.get("from_date"):
		conditions.append(f"and start_date >= '{filters.from_date}'")

	if filters.get("to_date"):
		conditions.append(f"and end_date <= '{filters.to_date}'")

	if filters.get("company"):
		conditions.append(f"and company = '{filters.company}'")

	if filters.get("employee"):
		conditions.append(f"and employee = '{filters.employee}'")

	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions.append(f"and currency = '{filters.currency}'")
	
	if filters.get("project"):
		projects = filters.get("project")
		if len(projects) == 1:
			conditions.append(f"and project = '{projects[0]}'")
		elif len(projects) > 1:	
			project_tuple = tuple(projects)
			conditions.append(f"and project IN {project_tuple}")

	if filters.get("department"):
		conditions.append(f"and department = '{filters.department}'")		

	con = "{}".format(" ".join(conditions)) if conditions else ""

	salary_slips = frappe.db.sql(
					"""
					select *
					from `tabSalary Slip`
					where {conditions}
				""".format(
						conditions=con,
					),
					as_dict=1,
				)
	
	return salary_slips or []