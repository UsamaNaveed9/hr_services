# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
	get_data,
	get_period_list,
)

def execute(filters=None):
	columns = get_columns()
	data = get_full_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"label": _("Particulars"), "fieldname": "particulars", "fieldtype": "Data", "width": 400},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 200},
	]
	
	return columns

def get_full_data(filters):
	# Fetch customers according to projects
	projects = frappe.get_all('Project', 
							filters={'status': 'Open'}, 
							fields=['name', 'project_name','erc_fee'],
							order_by='name')

	data = []
	mis_data = [] #Monthly Income Statement data

	for row in projects:
		#get month start date and month end date on the basis of fiscal year and month name
		month_name = filters.get("month")
		fiscal_year = filters.get("fiscal_year")
		month_map = get_month_map()
		today = frappe.utils.getdate()
		from_date = today.replace(day=1, month=int(month_map[month_name]), year=int(fiscal_year))
		to_date = frappe.utils.get_last_day(from_date)

		if row.name == 'PROJ-0001':
			# 'Misk Full Time'
			full_time_employees = frappe.get_all('Employee',
							  		filters={'project': row.name,'employment_type': 'Full-time'}, 
									fields=['name', 'employee_name','project','project_name'])
			
			ft_no_of_emp = 0 #ft for full time
			full_timers_total = 0.0 #revenue will calculate 8% of each employee if invoice issued
			for emp in full_time_employees:
				sales_invoices = frappe.db.sql(
					"""select si.total,si.name
					from `tabSales Invoice Item` si_item, `tabSales Invoice` si
					where si_item.parent = si.name
					and si_item.employee_id = %s
					and si.posting_date >= %s
					and si.posting_date <= %s
					and si.docstatus = 1
					and si.remarks LIKE %s
					""",
					(emp.name, from_date, to_date, '%Payroll Invoice%'),
					as_dict=True
				)
				# Check if any records were found for the employee
				if sales_invoices:
					ft_no_of_emp += 1
					for sal_inv in sales_invoices:
						total_value = sal_inv['total']
						full_timers_total += total_value
			
			full_timer_revenue = (full_timers_total / 1.08) * 0.08
			#Misk Full time employees row append into data
			data.append({"project_name": "Misk Full Time", "no_of_emps": ft_no_of_emp, "erc_fee": "8%", "total_revenue": full_timer_revenue})

			# 'Misk Part Time'
			part_time_employees = frappe.get_all('Employee',
							  		filters={'project': row.name,'employment_type': 'Part-time'},
									fields=['name', 'employee_name','project','project_name'])
				
			pt_no_of_emp = 0 #pt for part time
			part_timers_total = 0.0 #revenue will calculate 8% of each employee if invoice issued
			for emp in part_time_employees:
				sales_invoices = frappe.db.sql(
					"""select si.total,si.name
					from `tabSales Invoice Item` si_item, `tabSales Invoice` si
					where si_item.parent = si.name
					and si_item.employee_id = %s
					and si.posting_date >= %s
					and si.posting_date <= %s
					and si.docstatus = 1
					and si.remarks LIKE %s
					""",
					(emp.name, from_date, to_date, '%Payment For Part Timer%'),
					as_dict=True
				)
				
				# Check if any records were found for the employee
				if sales_invoices:
					pt_no_of_emp += 1
					for sal_inv in sales_invoices:
						total_value = sal_inv['total']
						part_timers_total += total_value
			
			part_timer_revenue = (part_timers_total / 1.08) * 0.08
			#Misk part time employees row append into data
			data.append({"project_name": "Misk Part Time", "no_of_emps": pt_no_of_emp, "erc_fee": "8%", "total_revenue": part_timer_revenue})
		elif row.name != 'PROJ-0018': #ignoring Elite HQ
			# Fetch employees according to projects
			employees = frappe.get_all('Employee',
							  		filters={'project': row.name}, 
									fields=['name', 'employee_name','project','project_name','status','relieving_date'])
			emps_count = 0
			for emp in employees:
				if emp.status == "Active":
					emps_count += 1
				else:
					if emp.relieving_date and from_date <= emp.relieving_date <= to_date:
						emps_count +=1
			
			row["no_of_emps"] = emps_count
			row["total_revenue"] = emps_count * row.erc_fee
			row["erc_fee"] = frappe.utils.fmt_money(row.erc_fee, currency="", precision=2)
			data.append(row)
	
	# total_row = {
	# 	"project_name": '<strong>Total </strong>',
	# 	"no_of_emps": sum(row["no_of_emps"] for row in data),
	# 	"erc_fee": "",
	# 	"total_revenue": sum(row["total_revenue"] for row in data)
	# }
	#Append Revenue row
	total_revenue = sum(row["total_revenue"] for row in data)
	revenue_row = {"particulars": "Revenue","amount": total_revenue, "indent": 0.0}
	mis_data.append(revenue_row)
	#Append project wise breakdown under revenue
	for row in data:
		projectwise_rows = {"particulars": row["project_name"] ,"amount": row["total_revenue"] , "indent": 1.0}
		mis_data.append(projectwise_rows)

	cogs_row = {"particulars": "COGS","amount": 0}
	mis_data.append(cogs_row)
	gross_row = {"particulars": '<strong>Gross Profit </strong>',"amount": total_revenue}
	mis_data.append(gross_row)
	#empty row
	empty_row = {}
	mis_data.append(empty_row)

	#parameters for period list
	filter_based_on = "Date Range"
	period_start_date = from_date
	period_end_date = to_date
	periodicity = "Monthly"
	from_fiscal_year = fiscal_year
	to_fiscal_year = fiscal_year

	period_list = get_period_list(
		from_fiscal_year,
		to_fiscal_year,
		period_start_date,
		period_end_date,
		filter_based_on,
		periodicity,
		company=filters.get("company"),
	)
	#frappe.errprint(period_list)
	#getting all accounts that have the root type Expense
	expense = get_data(
		filters.company,
		"Expense",
		"Debit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)

	#Manpower Expense BreakDown
	manpower_row = {"particulars": "G&A Manpower Expense","amount": 0,  "indent": 0.0}
	mis_data.append(manpower_row)
	total_of_manpower_expense = 0.0
	#append those expense account that have expense category as Manpower Expense
	for acc_row in expense:
		if "account" in acc_row and frappe.db.exists("Account", {"name": acc_row["account"], "is_group": 0, "custom_expense_category": "Manpower Expense"}):
			total_of_manpower_expense += acc_row["total"]
			mis_data.append({"particulars": acc_row["account_name"] ,"amount": acc_row["total"],  "indent": 1.0})

	manpower_row["amount"] = total_of_manpower_expense

	#Other Expense BreakDown
	other_exp_row = {"particulars": "Other Expense","amount":0,  "indent": 0.0}
	mis_data.append(other_exp_row)
	total_of_other_expense = 0.0
	#append those expense account that have expense category as Other Expense
	for acc_row in expense:
		if "account" in acc_row and frappe.db.exists("Account", {"name": acc_row["account"], "is_group": 0, "custom_expense_category": "Other Expense"}):
			total_of_other_expense += acc_row["total"]
			mis_data.append({"particulars": acc_row["account_name"] ,"amount": acc_row["total"],  "indent": 1.0})
	
	other_exp_row["amount"] = total_of_other_expense
	#append total expense row
	total_expense = total_of_manpower_expense + total_of_other_expense
	total_expense_row = {"particulars": '<strong>Total Expense </strong>',"amount": total_expense}
	mis_data.append(total_expense_row)
	#empty row
	mis_data.append(empty_row)
	operating_profit = total_revenue - total_expense  
	operating_profit_row = {"particulars": '<strong>Operating Profit </strong>',"amount": operating_profit}
	mis_data.append(operating_profit_row)
	#empty row
	mis_data.append(empty_row)
	income_loss_row = {"particulars": "Other income/loss","amount": 0}
	mis_data.append(income_loss_row)
	net_income_row = {"particulars": '<strong>Net Income - Monthly </strong>',"amount": operating_profit}
	mis_data.append(net_income_row)
	
	return mis_data

def get_month_map():
	return frappe._dict({
		"January": 1,
		"February": 2,
		"March": 3,
		"April": 4,
		"May": 5,
		"June": 6,
		"July": 7,
		"August": 8,
		"September": 9,
		"October": 10,
		"November": 11,
		"December": 12
	})