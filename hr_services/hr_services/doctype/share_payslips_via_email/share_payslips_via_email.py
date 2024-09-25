# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json

class SharePayslipsviaEmail(Document):
	pass

@frappe.whitelist()
def get_employees(project,start_date,end_date):
	employees = frappe.get_all('Employee', filters={'status': 'Active', 'project':project}, fields=['name','employee_name','personal_email'])

	filtered_employees = []
	for employee in employees:
		salary_slip = frappe.get_value(
			"Salary Slip",
			filters={"employee": employee["name"], "custom_email_sent": 0,"start_date": start_date, "end_date": end_date, "docstatus": 1},
			fieldname="name",
		)
		if salary_slip:
			employee["salary_slip"] = salary_slip
			filtered_employees.append(employee)
	if not filtered_employees:
		frappe.throw(_("No Unsend Salary slip exists in the period from {0} to {1}".format(start_date,end_date)))

	return filtered_employees

@frappe.whitelist()
def send_emails(employees,month_name,year):
	emps = json.loads(employees)
	for emp in emps:
		receiver = emp['email']
		message = "Dear {0},<br><br>Please find attached your payslip for the month of {1}, {2}.<br><br>Best regards,<br>Elite Resources Center".format(emp['employee_name'],month_name,year)
		password = None
		salary_slip = frappe.get_doc("Salary Slip",emp['salary_slip'])

		email_args = {
			"recipients": [receiver],
			"message": _(message),
			"subject": "Salary Slip - {0} {1}".format(month_name, year),
			"attachments": [
				frappe.attach_print(salary_slip.doctype, salary_slip.name, file_name=salary_slip.name, password=password)
			],
			"reference_doctype": salary_slip.doctype,
			"reference_name": salary_slip.name,
		}
		
		frappe.sendmail(**email_args)

		salary_slip.custom_email_sent = 1
		salary_slip.save(ignore_permissions=True)

	return True	
