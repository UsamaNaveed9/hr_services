# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json

class PayrollInvoicesGenerator(Document):
	pass

@frappe.whitelist()
def get_employees(project,start_date,end_date,month_name):
	employees = frappe.get_all('Employee', filters={'status': 'Active', 'project':project}, fields=['name','employee_name'])

	filtered_employees = []
	if project != "PROJ-0007": #if project not equal to Alhokair
		for employee in employees:
			salary_slip = frappe.get_value(
				"Salary Slip",
				filters={"employee": employee["name"], "invoice_created": 0,"start_date": start_date, "end_date": end_date, "docstatus": 1},
				fieldname="name",
			)
			if salary_slip:
				employee["salary_slip"] = salary_slip
				filtered_employees.append(employee)
		if not filtered_employees:
			frappe.throw(_("No Salary slip exists in the period from {0} to {1}".format(start_date,end_date)))
	elif project == "PROJ-0007": #if project equal to Alhokair
		for employee in employees:
			if not frappe.db.exists("Payroll Processed",{"employee": employee["name"],"month_name":month_name,"project": project}):
				filtered_employees.append(employee)

	return filtered_employees

@frappe.whitelist()
def get_employees_misk(project,start_date,end_date,type):
	employees = frappe.get_all('Employee', filters={'status': 'Active', 'project':project,'employment_type': type}, fields=['name','employee_name'])

	filtered_employees = []
	for employee in employees:
		salary_slip = frappe.get_value(
			"Salary Slip",
			filters={"employee": employee["name"], "invoice_created": 0,"start_date": start_date, "end_date": end_date, "docstatus": 1},
			fieldname="name",
		)
		if salary_slip:
			employee["salary_slip"] = salary_slip
			filtered_employees.append(employee)

	for emp in filtered_employees:
		po_mgt_list = frappe.db.get_list('PO Management',
							filters={
								'status': 'Active',
								'docstatus': 1,
								'employee_no': emp["name"],
								'project_no': 'PROJ-0001'
							},
							fields=['name'],
							order_by='creation asc'
						)
		rem_units = 0
		for po_mgt in po_mgt_list:
			po_mdoc = frappe.get_doc("PO Management", po_mgt.name)
			rem_units = rem_units + po_mdoc.remaining_units
		
		if rem_units > 0:
			emp["remaining_units"] = rem_units
	if not filtered_employees:
		frappe.throw(_("No Salary slip exists in the period from {0} to {1}".format(start_date,end_date)))

	return filtered_employees


@frappe.whitelist()
def generate_invoices(project,due_date,customer,invoice_type,employees,month_name,my_in_arabic,year):
	emps = json.loads(employees)
	if invoice_type == "One Invoice with all employees details":
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.project = project
		si.is_pos = 0

		for emp in emps:
			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 34
			si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
			si_item.qty = 1
			nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
			added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")
			
			housing_adv_loan = 0
			sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
			if sslp_doc.loans:
				for loan in sslp_doc.loans:
					if loan.loan_type == "Housing Advance":
						housing_adv_loan = housing_adv_loan + loan.total_payment

			if nationality == "Saudi Arabia" and added_to_gosi == 1:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				si_item.rate = net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975)
			else:
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				si_item.rate = net_pay + loan_repay - housing_adv_loan
				
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

		si.remarks = "Payroll Invoice"
		si.save(ignore_permissions=True)

		if si.name:
			for emp in emps:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
			status = True

	elif invoice_type == "One Invoice with all employees details sumup each emp in one line":
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.project = project
		si.is_pos = 0

		for emp in emps:
			total_mp = 0
			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 34
			si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
			si_item.qty = 1
			nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
			added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

			housing_adv_loan = 0
			sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
			if sslp_doc.loans:
				for loan in sslp_doc.loans:
					if loan.loan_type == "Housing Advance":
						housing_adv_loan = housing_adv_loan + loan.total_payment

			if nationality == "Saudi Arabia" and added_to_gosi == 1:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				total_mp = net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975)
			else:
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				total_mp = net_pay + loan_repay - housing_adv_loan
				
			si_item.employee_id = emp["employee"]
			si_item.employee_name = emp["employee_name"]

			if nationality == "Saudi Arabia":
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				total_mp = total_mp + ((basic + housing) * 0.1175)
			else:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				total_mp = total_mp + ((basic + housing) * 0.02)

			total_mp = total_mp + frappe.db.get_value("Project", {"name":project}, "erc_fee")
			si_item.rate = total_mp
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

		si.remarks = "Payroll Invoice"
		si.save(ignore_permissions=True)

		if si.name:
			for emp in emps:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
			status = True

	elif invoice_type == "One Invoice with all employees total one line only":
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.project = project
		si.is_pos = 0
		total_mp = 0

		for emp in emps:
			nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
			added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

			housing_adv_loan = 0
			sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
			if sslp_doc.loans:
				for loan in sslp_doc.loans:
					if loan.loan_type == "Housing Advance":
						housing_adv_loan = housing_adv_loan + loan.total_payment

			if nationality == "Saudi Arabia" and added_to_gosi == 1:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				total_mp = total_mp + (net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975))
			else:
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				total_mp = total_mp + net_pay + loan_repay - housing_adv_loan

			if nationality == "Saudi Arabia":
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				total_mp = total_mp + ((basic + housing) * 0.1175)
			else:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				total_mp = total_mp + ((basic + housing) * 0.02)

			total_mp = total_mp + frappe.db.get_value("Project", {"name":project}, "erc_fee")
			total_mp = total_mp + frappe.db.get_value("Project", {"name":project}, "bt_charges")

		si_item = frappe.new_doc("Sales Invoice Item")
		si_item.item_code = 34
		si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
		si_item.qty = 1
		si_item.rate = total_mp
		si.append("items", si_item)

		si_tax = frappe.new_doc("Sales Taxes and Charges")
		si_tax.charge_type = "On Net Total"
		si_tax.account_head = "VAT 15% - ERC"
		si_tax.description = "VAT 15%"
		si_tax.rate = 15
		si.append("taxes", si_tax)

		si.remarks = "Payroll Invoice"
		si.save(ignore_permissions=True)

		if si.name:
			for emp in emps:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
			status = True
	
	elif invoice_type == "One Invoice with all employees total one line only without gosi and btc":
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.project = project
		si.is_pos = 0
		total_mp = 0

		for emp in emps:
			housing_adv_loan = 0
			sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
			if sslp_doc.loans:
				for loan in sslp_doc.loans:
					if loan.loan_type == "Housing Advance":
						housing_adv_loan = housing_adv_loan + loan.total_payment

			net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
			loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
			total_mp = total_mp + net_pay + loan_repay - housing_adv_loan
			total_mp = total_mp + frappe.db.get_value("Employee", {"name":emp["employee"]}, "custom_elite_monthly_fee")

		si_item = frappe.new_doc("Sales Invoice Item")
		si_item.item_code = 34
		si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
		si_item.qty = 1
		si_item.rate = total_mp
		si.append("items", si_item)

		si_tax = frappe.new_doc("Sales Taxes and Charges")
		si_tax.charge_type = "On Net Total"
		si_tax.account_head = "VAT 15% - ERC"
		si_tax.description = "VAT 15%"
		si_tax.rate = 15
		si.append("taxes", si_tax)

		si.remarks = "Payroll Invoice"
		si.save(ignore_permissions=True)

		if si.name:
			for emp in emps:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
			status = True		

	elif invoice_type == "Invoice based on per PO":
		#frappe.errprint(emps)
		po_list = []
		for emp in emps:
			po_no = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no")
			if po_no not in po_list:
				po_list.append(po_no)
		for po in po_list:
			si = frappe.new_doc("Sales Invoice")
			si.customer = customer
			si.set_posting_time = 1
			si.posting_date = due_date
			si.due_date = due_date
			si.issue_date = due_date
			si.project = project
			si.is_pos = 0
			si.po_no = po
			qty = 0
			for emp in emps:
				si.print_customer = frappe.db.get_value("Employee", {"name":emp["employee"]}, "print_customer_for_invoice")
				if po == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no"):
					qty += 1
					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.qty = 1
					nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
					added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

					housing_adv_loan = 0
					sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
					if sslp_doc.loans:
						for loan in sslp_doc.loans:
							if loan.loan_type == "Housing Advance":
								housing_adv_loan = housing_adv_loan + loan.total_payment

					if nationality == "Saudi Arabia" and added_to_gosi == 1:
						basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
						housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
						net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
						loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
						si_item.rate = net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975)
					else:
						net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
						loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
						si_item.rate = net_pay + loan_repay - housing_adv_loan
						
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
			si_item.qty = qty
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "erc_fee")
			si.append("items", si_item)

			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 419
			si_item.qty = qty
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "bt_charges")
			si.append("items", si_item)

			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.remarks = "Payroll Invoice"
			si.save(ignore_permissions=True)

			if si.name:
				for emp in emps:
					if po == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no"):
						sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
						sal_slip.invoice_created = 1
						sal_slip.save(ignore_permissions=True)
				status = True

	elif invoice_type == "Invoice based on per Employee":
		for emp in emps:
			si = frappe.new_doc("Sales Invoice")
			si.customer = customer
			si.set_posting_time = 1
			si.posting_date = due_date
			si.due_date = due_date
			si.issue_date = due_date
			si.project = project
			si.is_pos = 0

			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 34
			si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
			si_item.qty = 1
			nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
			added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

			housing_adv_loan = 0
			sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
			if sslp_doc.loans:
				for loan in sslp_doc.loans:
					if loan.loan_type == "Housing Advance":
						housing_adv_loan = housing_adv_loan + loan.total_payment

			if nationality == "Saudi Arabia" and added_to_gosi == 1:
				basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
				housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				si_item.rate = net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975)
			else:
				net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
				loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
				si_item.rate = net_pay + loan_repay - housing_adv_loan
				
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
			si_item.qty = 1
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "erc_fee")
			si.append("items", si_item)

			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 419
			si_item.qty = 1
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "bt_charges")
			si.append("items", si_item)

			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.remarks = "Payroll Invoice"
			si.save(ignore_permissions=True)

			if si.name:
				sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
				sal_slip.invoice_created = 1
				sal_slip.save(ignore_permissions=True)
				status = True

	elif invoice_type == "Invoice based on per PO with other POs":
		po_list = []
		po_for_rota_list = []
		po_for_neom_list = []
		for emp in emps:
			po_no = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no")
			if po_no not in po_list:
				po_list.append(po_no)

			po_for_re = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_rotation_expense")
			if po_for_re == 1:
				po_no_for_re = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no_for_rotation")
				if po_no_for_re not in po_for_rota_list:
					po_for_rota_list.append(po_no_for_re)

			po_for_na = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_neom_allowance")
			if po_for_na == 1:
				po_no_for_na = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no_for_neom")
				if po_no_for_na not in po_for_neom_list:
					po_for_neom_list.append(po_no_for_na)		

		#frappe.errprint(po_list)
		#frappe.errprint(po_for_rota_list)
		#frappe.errprint(po_for_neom_list)

		for po_rota in po_for_rota_list:
			si = frappe.new_doc("Sales Invoice")
			si.customer = customer
			si.set_posting_time = 1
			si.posting_date = due_date
			si.due_date = due_date
			si.issue_date = due_date
			si.project = project
			si.is_pos = 0
			si.po_no = po_rota
			for emp in emps:
				if po_rota == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no_for_rotation"):
					po_for_re = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_rotation_expense")
					sc_for_rotation = frappe.db.get_value("Employee", {"name":emp["employee"]}, "s_c_for_rotation")
					if po_for_re == 1 and frappe.db.exists("Salary Detail",{"parent": emp["salary_slip"],"salary_component": sc_for_rotation}):
						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 912
						si_item.qty = 1
						si_item.rate = float(frappe.db.get_value("Salary Detail", {"parent":emp["salary_slip"], "salary_component": sc_for_rotation}, "amount"))
						si_item.employee_id = emp["employee"]
						si_item.employee_name = emp["employee_name"]
						if si_item.rate > 0.0:
							si.append("items", si_item)

						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 915
						si_item.qty = 1
						si_item.rate = float(frappe.db.get_value("Salary Detail", {"parent":emp["salary_slip"], "salary_component": sc_for_rotation}, "amount")) * 0.1
						si_item.employee_id = emp["employee"]
						si_item.employee_name = emp["employee_name"]
						if si_item.rate > 0.0:
							si.append("items", si_item)

			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.remarks = "Payroll Invoice"
			#if items exist then invoice save in the system otherwise skip it.
			if len(si.items) > 0:
				si.save(ignore_permissions=True)

		for po_neom in po_for_neom_list:
			si = frappe.new_doc("Sales Invoice")
			si.customer = customer
			si.set_posting_time = 1
			si.posting_date = due_date
			si.due_date = due_date
			si.issue_date = due_date
			si.project = project
			si.is_pos = 0
			si.po_no = po_neom
			for emp in emps:
				if po_neom == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no_for_neom"):
					po_for_na = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_neom_allowance")
					sc_for_neom = frappe.db.get_value("Employee", {"name":emp["employee"]}, "s_c_for_neom")
					if po_for_na == 1 and frappe.db.exists("Salary Detail",{"parent": emp["salary_slip"],"salary_component": sc_for_neom}):
						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 916
						si_item.qty = 1
						si_item.rate = frappe.db.get_value("Salary Detail", {"parent":emp["salary_slip"], "salary_component": sc_for_neom}, "amount")
						si_item.employee_id = emp["employee"]
						si_item.employee_name = emp["employee_name"]
						if si_item.rate > 0.0:
							si.append("items", si_item)

			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.remarks = "Payroll Invoice"
			#if items exist then invoice save in the system otherwise skip it.
			if len(si.items) > 0:
				si.save(ignore_permissions=True)
		
		for po in po_list:
			si = frappe.new_doc("Sales Invoice")
			si.customer = customer
			si.set_posting_time = 1
			si.posting_date = due_date
			si.due_date = due_date
			si.issue_date = due_date
			si.project = project
			si.is_pos = 0
			si.po_no = po
			qty = 0
			for emp in emps:
				if po == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no"):
					qty += 1
					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.qty = 1
					manpower = 0
					nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
					added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

					housing_adv_loan = 0
					sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
					if sslp_doc.loans:
						for loan in sslp_doc.loans:
							if loan.loan_type == "Housing Advance":
								housing_adv_loan = housing_adv_loan + loan.total_payment

					if nationality == "Saudi Arabia" and added_to_gosi == 1:
						basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
						housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
						net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
						loan_repay = float(frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment"))
						manpower = manpower + net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975)
					else:
						net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
						loan_repay = float(frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment"))
						manpower = manpower + net_pay + loan_repay - housing_adv_loan

					po_for_re = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_rotation_expense")
					sc_for_rotation = ""
					if po_for_re == 1:
						sc_for_rotation = frappe.db.get_value("Employee", {"name":emp["employee"]}, "s_c_for_rotation")
						re_amount = frappe.db.get_value("Salary Detail", {"parent":emp["salary_slip"], "salary_component": sc_for_rotation}, "amount")
						if re_amount:
							manpower = manpower - re_amount

					po_for_na = frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_for_neom_allowance")
					sc_for_neom = ""
					if po_for_na == 1:
						sc_for_neom = frappe.db.get_value("Employee", {"name":emp["employee"]}, "s_c_for_neom")
						na_amount = frappe.db.get_value("Salary Detail", {"parent":emp["salary_slip"], "salary_component": sc_for_neom}, "amount")
						if na_amount:
							manpower = manpower - na_amount

					si_item.rate = manpower	
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
			si_item.qty = qty
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "erc_fee")
			si.append("items", si_item)

			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = 419
			si_item.qty = qty
			si_item.rate = frappe.db.get_value("Project", {"name":project}, "bt_charges")
			si.append("items", si_item)

			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.remarks = "Payroll Invoice"
			si.save(ignore_permissions=True)

			if si.name:
				for emp in emps:
					if po == frappe.db.get_value("Employee", {"name":emp["employee"]}, "po_no"):
						sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
						sal_slip.invoice_created = 1
						sal_slip.save(ignore_permissions=True)
				status = True

	elif invoice_type == "One Invoice with all employees total dept wise one line only":
		dept_list = []
		loc_list = []
		for emp in emps:
			dept = frappe.db.get_value("Employee", {"name":emp["employee"]}, "department")
			loc = frappe.db.get_value("Employee", {"name":emp["employee"]}, "custom_location")
			if dept and dept not in dept_list:
				dept_list.append(dept)

			if loc and loc not in loc_list:
				loc_list.append(loc)	
		
		for dp in dept_list:
			for lc in loc_list:
				total_mp = 0
				for emp in emps:
					emp_dp = frappe.db.get_value("Employee", {"name":emp["employee"]}, "department")
					emp_loc = frappe.db.get_value("Employee", {"name":emp["employee"]}, "custom_location")
					if dp == emp_dp and lc == emp_loc:
						#manpower adding into total_mp
						nationality = frappe.db.get_value("Employee", {"name":emp["employee"]}, "nationality")
						added_to_gosi = frappe.db.get_value("Employee", {"name":emp["employee"]}, "added_to_gosi")

						housing_adv_loan = 0
						sslp_doc = frappe.get_doc("Salary Slip",emp["salary_slip"])
						if sslp_doc.loans:
							for loan in sslp_doc.loans:
								if loan.loan_type == "Housing Advance":
									housing_adv_loan = housing_adv_loan + loan.total_payment

						if nationality == "Saudi Arabia" and added_to_gosi == 1:
							basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
							housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
							net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
							loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
							total_mp = total_mp + (net_pay + loan_repay - housing_adv_loan + ((basic + housing) * 0.0975))
						else:
							net_pay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "net_pay")
							loan_repay = frappe.db.get_value("Salary Slip", {"name":emp["salary_slip"]}, "total_loan_repayment")
							total_mp = total_mp + net_pay + loan_repay - housing_adv_loan
						#gosi adding into total_mp
						if nationality == "Saudi Arabia":
							basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
							housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
							total_mp = total_mp + ((basic + housing) * 0.1175)
						else:
							basic = frappe.db.get_value("Employee", {"name":emp["employee"]}, "basic_salary")
							housing = frappe.db.get_value("Employee", {"name":emp["employee"]}, "housing_allowance")
							total_mp = total_mp + ((basic + housing) * 0.02)
						#erc fee and bank charges adding into total_mp
						total_mp = total_mp + frappe.db.get_value("Project", {"name":project}, "erc_fee")
						total_mp = total_mp + frappe.db.get_value("Project", {"name":project}, "bt_charges")
				if total_mp > 0:		
					si = frappe.new_doc("Sales Invoice")
					si.customer = customer
					si.set_posting_time = 1
					si.posting_date = due_date
					si.due_date = due_date
					si.issue_date = due_date
					si.project = project
					si.is_pos = 0

					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.item_name = f"{dp} - {lc}"
					si_item.qty = 1
					si_item.rate = total_mp
					si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.remarks = "Payroll Invoice"
					si.save(ignore_permissions=True)

					if si.name:
						for emp in emps:
							sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
							sal_slip.invoice_created = 1
							sal_slip.save(ignore_permissions=True)
						status = True
	
	elif invoice_type == "Division(dept) wise invoices Alhokair":
		dept_list = []
		for emp in emps:
			dept = frappe.db.get_value("Employee", {"name":emp["employee"]}, "department")
			if dept and dept not in dept_list:
				dept_list.append(dept)

		for dept in dept_list:
			no_emps_of_dept = 0
			slted_emps = []
			for emp in emps:
				emp_dp = frappe.db.get_value("Employee", {"name":emp["employee"]}, "department")
				if dept == emp_dp:
					no_emps_of_dept += 1
					slted_emps.append(emp["employee"])
		
			#frappe.errprint(dept)
			#frappe.errprint(no_emps_of_dept)
			#frappe.errprint(slted_emps)
			if dept != "Holding Bus Tour":
				if no_emps_of_dept > 0 and slted_emps:		
					si = frappe.new_doc("Sales Invoice")
					si.customer = customer
					si.set_posting_time = 1
					si.posting_date = due_date
					si.due_date = due_date
					si.issue_date = due_date
					si.project = project
					si.is_pos = 0

					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.item_name = f"{dept} - Operational Cost of employees"
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.qty = no_emps_of_dept
					si_item.rate = frappe.db.get_value("Department", {"name":dept}, "custom_month_erc_cost")
					si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.remarks = "Payroll Invoice"
					si.save(ignore_permissions=True)

					if si.name:
						for s_emp in slted_emps:
							pp = frappe.new_doc("Payroll Processed")
							pp.employee = s_emp
							pp.employee_name = frappe.db.get_value("Employee", {"name":emp["employee"]}, "employee_name")
							pp.month_name = month_name
							pp.project = project
							pp.project_name = frappe.db.get_value("Project", {"name":project}, "project_name")
							pp.save(ignore_permissions=True)
			elif dept == "Holding Bus Tour":
				if no_emps_of_dept > 0 and slted_emps:		
					si = frappe.new_doc("Sales Invoice")
					si.customer = customer
					si.set_posting_time = 1
					si.posting_date = due_date
					si.due_date = due_date
					si.issue_date = due_date
					si.project = project
					si.is_pos = 0

					for s_emp in slted_emps:
						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 34
						si_item.item_name = f"{dept} - Operational Cost of employees"
						si_item.description = f"ERC for the month of {month_name} {year}\nERC لشهر {my_in_arabic}"
						si_item.employee_id = s_emp
						si_item.qty = 1
						si_item.rate = frappe.db.get_value("Department", {"name":dept}, "custom_month_erc_cost")
						si.append("items", si_item)

						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 781
						si_item.qty = 1
						nationality = frappe.db.get_value("Employee", {"name":s_emp}, "nationality")
						if nationality == "Saudi Arabia":
							basic = frappe.db.get_value("Employee", {"name":s_emp}, "basic_salary")
							housing = frappe.db.get_value("Employee", {"name":s_emp}, "housing_allowance")
							si_item.rate = (basic + housing) * 0.1175
						else:
							basic = frappe.db.get_value("Employee", {"name":s_emp}, "basic_salary")
							housing = frappe.db.get_value("Employee", {"name":s_emp}, "housing_allowance")
							si_item.rate = (basic + housing) * 0.02

						si_item.employee_id = s_emp
						si_item.employee_name = frappe.db.get_value("Employee", {"name":s_emp}, "employee_name")
						si.append("items", si_item)

						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = 632
						si_item.employee_id = s_emp
						si_item.qty = 1
						si_item.rate = 125
						si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.remarks = "Payroll Invoice"
					si.save(ignore_permissions=True)

					if si.name:
						for s_emp in slted_emps:
							pp = frappe.new_doc("Payroll Processed")
							pp.employee = s_emp
							pp.employee_name = frappe.db.get_value("Employee", {"name":s_emp}, "employee_name")
							pp.month_name = month_name
							pp.project = project
							pp.project_name = frappe.db.get_value("Project", {"name":project}, "project_name")
							pp.save(ignore_permissions=True)

		status = True
	
	#only for misk client 
	if project == "PROJ-0001":
		for emp in emps:
			po_mgt_list = frappe.db.get_list('PO Management',
							filters={
								'status': 'Active',
								'docstatus': 1,
								'employee_no': emp["employee"],
								'project_no': 'PROJ-0001'
							},
							fields=['name'],
							order_by='creation asc'
						)

			r_wd = emp["working_days"]
			for po_mgt in po_mgt_list:
				po_mdoc = frappe.get_doc("PO Management", po_mgt.name)
				invoicing_rate = po_mdoc.invoicing_rate
				used_units = po_mdoc.used_units
				remaining_units = po_mdoc.remaining_units

				if remaining_units >= r_wd and r_wd != 0:
					#rate = r_wd * invoicing_rate
					diff_units = remaining_units - r_wd
					used_units = used_units + r_wd

					si = frappe.new_doc("Sales Invoice")
					si.customer = customer
					si.set_posting_time = 1
					si.posting_date = due_date
					si.due_date = due_date
					si.issue_date = due_date
					si.project = project
					si.is_pos = 0
					si.print_customer = frappe.db.get_value("Employee", {"name":emp["employee"]}, "print_customer_for_invoice")
					si.po_no = po_mdoc.po_no

					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.qty = r_wd
					si_item.rate = invoicing_rate
					si_item.employee_id = emp["employee"]
					si_item.employee_name = emp["employee_name"]
					si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.remarks = "Payroll Invoice"
					si.save(ignore_permissions=True)
					
					if si.name:
						sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
						sal_slip.invoice_created = 1
						sal_slip.save(ignore_permissions=True)
					
					r_wd = 0
					po_mdoc.used_units = used_units
					po_mdoc.remaining_units = diff_units
					po_mdoc.save(ignore_permissions=True)
					if po_mdoc.remaining_units == 0:
						po_mdoc.status = "Completed"
						po_mdoc.save(ignore_permissions=True)
					status = True	

				elif r_wd > remaining_units:
					#rate = remaining_units * invoicing_rate
					r_wd = r_wd - remaining_units
					used_units = used_units + remaining_units

					si = frappe.new_doc("Sales Invoice")
					si.customer = customer
					si.set_posting_time = 1
					si.posting_date = due_date
					si.due_date = due_date
					si.issue_date = due_date
					si.project = project
					si.is_pos = 0
					si.print_customer = frappe.db.get_value("Employee", {"name":emp["employee"]}, "print_customer_for_invoice")
					si.po_no = po_mdoc.po_no

					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.description = f"Manpower cost for the month of {month_name} {year}\nتكلفة القوى العامله لشهر {my_in_arabic}"
					si_item.qty = remaining_units
					si_item.rate = invoicing_rate
					si_item.employee_id = emp["employee"]
					si_item.employee_name = emp["employee_name"]
					si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.remarks = "Payroll Invoice"
					si.save(ignore_permissions=True)

					if si.name:
						sal_slip = frappe.get_doc("Salary Slip", emp["salary_slip"])
						sal_slip.invoice_created = 1
						sal_slip.save(ignore_permissions=True)

					remaining_units = 0
					po_mdoc.used_units = used_units
					po_mdoc.remaining_units = remaining_units
					po_mdoc.save(ignore_permissions=True)
					if po_mdoc.remaining_units == 0:
						po_mdoc.status = "Completed"
						po_mdoc.save(ignore_permissions=True)
					status = True
	return status