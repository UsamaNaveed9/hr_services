# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
import json
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry,get_existing_salary_slips

@frappe.whitelist()
def get_totals(self):
	#loading the frm data
	self = json.loads(self)
	#adding the employee id into emps list
	# emps = []
	# for emp in self["employees"]:
	# 	emps.append(emp["employee"])
	#getting the sum of gross pay, sum of total deductions, sum of net pay of all salary slips
	totals = frappe.db.sql("""
							SELECT 
								payroll_entry, 
								SUM(gross_pay) as total_gross,
						 		SUM(total_deduction) as total_deduction,
								SUM(net_pay) as total_net_pay,
								SUM(total_loan_repayment) as total_loan_repayment
							FROM
								`tabSalary Slip`
							WHERE 
					 			docstatus != 2
					 			AND payroll_entry = %s
							""", (self["name"]),
							as_dict=1)
	return totals

@frappe.whitelist()
def create_delete_salary_slip(payroll_name):
	payroll_doc = frappe.get_doc("Payroll Entry", payroll_name)

	employee_count = frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabPayroll Employee Detail`
		WHERE parent = %s
	""", payroll_name)[0][0]

	frappe.db.set_value("Payroll Entry", payroll_name, {"number_of_employees": employee_count}, update_modified=False)
	frappe.db.commit()

	employees = [emp.employee for emp in payroll_doc.employees]
	if employees:
		args = frappe._dict(
			{
				"salary_slip_based_on_timesheet": payroll_doc.salary_slip_based_on_timesheet,
				"payroll_frequency": payroll_doc.payroll_frequency,
				"start_date": payroll_doc.start_date,
				"end_date": payroll_doc.end_date,
				"company": payroll_doc.company,
				"posting_date": payroll_doc.posting_date,
				"deduct_tax_for_unclaimed_employee_benefits": payroll_doc.deduct_tax_for_unclaimed_employee_benefits,
				"deduct_tax_for_unsubmitted_tax_exemption_proof": payroll_doc.deduct_tax_for_unsubmitted_tax_exemption_proof,
				"payroll_entry": payroll_doc.name,
				"exchange_rate": payroll_doc.exchange_rate,
				"currency": payroll_doc.currency,
			}
		)

	salary_slips_exist_for = get_existing_salary_slips(employees, args)

	for emp in employees:
		if emp not in salary_slips_exist_for:
			args.update({"doctype": "Salary Slip", "employee": emp})
			frappe.get_doc(args).insert()

	salary_slips_not_in = get_existing_salary_slips_not_in(employees,args)

	for ss in salary_slips_not_in:
		frappe.delete_doc("Salary Slip",ss)

	frappe.msgprint("Updated successfully.")	


def get_existing_salary_slips_not_in(employees, args):
	return frappe.db.sql_list(
		"""
		select distinct name from `tabSalary Slip`
		where docstatus!= 2 and company = %s and payroll_entry = %s
			and start_date >= %s and end_date <= %s
			and employee not in (%s)
	"""
		% ("%s", "%s", "%s", "%s", ", ".join(["%s"] * len(employees))),
		[args.company, args.payroll_entry, args.start_date, args.end_date] + employees,
	)	