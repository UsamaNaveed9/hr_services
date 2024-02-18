# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
import json

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
								SUM(net_pay) as total_net_pay
							FROM
								`tabSalary Slip`
							WHERE 
					 			docstatus != 2
					 			AND payroll_entry = %s
							""", (self["name"]),
							as_dict=1)
	return totals
