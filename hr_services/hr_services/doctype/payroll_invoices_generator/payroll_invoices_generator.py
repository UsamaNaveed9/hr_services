# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class PayrollInvoicesGenerator(Document):
	pass

@frappe.whitelist()
def get_employees(project,start_date,end_date):
	employees = frappe.get_all('Employee', filters={'status': 'Active', 'project':project}, fields=['name','employee_name'])

	filtered_employees = []
	for employee in employees:
		salary_slip = frappe.get_value(
			"Salary Slip",
			filters={"employee": employee["name"], "invoice_created": 0,"start_date": start_date, "end_date": end_date},
			fieldname="name",
		)
		if salary_slip:
			employee["salary_slip"] = salary_slip
			filtered_employees.append(employee)
			
	return filtered_employees

@frappe.whitelist()
def generate_invoices(project,due_date,customer,invoice_type,employees):
	emps = json.loads(employees)
	if invoice_type == "One Invoice with all employees details":
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.project = project

		for emp in emps:
			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 34
			si_item.qty = 1
			si_item.rate = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
			si_item.employee_id = emp["employee"]
			si_item.employee_name = emp["employee_name"]
			si.append("items", si_item)

			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 781
			si_item.qty = 1
			nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
			if nationality == "Saudi Arabia":
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				si_item.rate = (basic + housing) * 0.1175
			else:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				si_item.rate = (basic + housing) * 0.02

			si_item.employee_id = emp["employee"]
			si_item.employee_name = emp["employee_name"]
			si.append("items", si_item)

		si_item = frappe.new_doc("Sales Invoice Item")
		si_item.item_code = 415
		si_item.qty = len(emps)
		si_item.rate = frappe.db.get_value("Project", {"name":project}, "erc_fee")
		si.append("items", si_item)

		si_item = frappe.new_doc("Sales Invoice Item")
		si_item.item_code = 419
		si_item.qty = len(emps)
		si_item.rate = frappe.db.get_value("Project", {"name":project}, "bt_charges")
		si.append("items", si_item)

		si_tax = frappe.new_doc("Sales Taxes and Charges")
		si_tax.charge_type = "On Net Total"
		si_tax.account_head = "VAT 15% - ERC"
		si_tax.description = "VAT 15%"
		si_tax.rate = 15
		si.append("taxes", si_tax)

		si.save()

		if si.name:
			for emp in emps:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
			status = True	

	return status