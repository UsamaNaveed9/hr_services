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
	#get month start date and month end date on the basis of fiscal year and month name
	if filters.get("periodicity") == "One Month":
		month_name = filters.get("from_month")
		fiscal_year = filters.get("fiscal_year")
		month_map = get_month_map()
		today = frappe.utils.getdate()
		from_date = today.replace(day=1, month=int(month_map[month_name]), year=int(fiscal_year))
		to_date = frappe.utils.get_last_day(from_date)
	elif filters.get("periodicity") == "Multi Months":
		start_month_name = filters.get("from_month")
		end_month_name = filters.get("to_month")
		fiscal_year = filters.get("fiscal_year")
		month_map = get_month_map()
		today = frappe.utils.getdate()
		#first date of start month name
		from_date = today.replace(day=1, month=int(month_map[start_month_name]), year=int(fiscal_year))
		#last date of end month name
		end_month_first_date = today.replace(day=1, month=int(month_map[end_month_name]), year=int(fiscal_year))
		to_date = frappe.utils.get_last_day(end_month_first_date)

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

	columns = get_columns(period_list)
	data = get_full_data(filters,from_date,to_date,period_list)
	return columns, data

def get_columns(period_list):
	columns = [
		{
			"fieldname": "account",
			"label": _("Particulars"),
			"fieldtype": "Data",
			"width": 300,
		}
	]
	for period in period_list:
		columns.append(
			{
				"fieldname": period.key,
				"label": period.label,
				"fieldtype": "Currency",
				"options": "currency",
				"width": 150,
			}
		)
	
	columns.append(
		{
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Currency",
			"width": 150,
			"options": "currency",
		}
	)

	return columns

def get_full_data(filters,from_date,to_date,period_list):
	# Fetch customers according to projects
	projects = frappe.get_all('Project', 
							filters={'status': 'Open'}, 
							fields=['name', 'project_name','erc_fee'],
							order_by='name')

	rev_data = []	#Revenue data
	exp_data = [] #Expense data
	othr_exp_data = [] #Other expense data
	full_data = [] #full report data
	
	for row in projects:
		if row.name == 'PROJ-0001':
			# 'Misk Full Time'
			full_time_employees = frappe.get_all('Employee',
							  		filters={'project': row.name,'employment_type': 'Full-time'}, 
									fields=['name', 'employee_name','project','project_name'])
			
			ft_no_of_emp = 0 #ft for full time
			#Misk Full time employees row append into data
			full_timers_row = {"project_name": "Misk Full Time", "no_of_emps": 0, "erc_fee": "8%", "total_revenue": 0.0}
			for period in period_list:
				full_timers_total_per_period = 0.0 #revenue will calculate 8% of each employee if invoice issued
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
						(emp.name, period.from_date, period.to_date, '%Payroll Invoice%'),
						as_dict=True
					)
					# Check if any records were found for the employee
					if sales_invoices:
						ft_no_of_emp += 1
						for sal_inv in sales_invoices:
							total_value = sal_inv['total']
							full_timers_total_per_period += total_value
				
				full_timers_revenue_per_period = (full_timers_total_per_period / 1.08) * 0.08
				full_timers_row[period.key] = full_timers_revenue_per_period
				full_timers_row["total_revenue"] += full_timers_revenue_per_period
			rev_data.append(full_timers_row)
			

			# 'Misk Part Time'
			part_time_employees = frappe.get_all('Employee',
							  		filters={'project': row.name,'employment_type': 'Part-time'},
									fields=['name', 'employee_name','project','project_name'])
				
			pt_no_of_emp = 0 #pt for part time
			#Misk part time employees row append into data
			part_timers_row = {"project_name": "Misk Part Time", "no_of_emps": 0, "erc_fee": "8%", "total_revenue": 0.0}
			for period in period_list:
				part_timers_total_per_period = 0.0 #revenue will calculate 8% of each employee if invoice issued
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
						(emp.name, period.from_date, period.to_date, '%Payment For Part Timer%'),
						as_dict=True
					)
					
					# Check if any records were found for the employee
					if sales_invoices:
						pt_no_of_emp += 1
						for sal_inv in sales_invoices:
							total_value = sal_inv['total']
							part_timers_total_per_period += total_value
				
				part_timers_revenue_per_period = (part_timers_total_per_period / 1.08) * 0.08
				part_timers_row[period.key] = part_timers_revenue_per_period
				part_timers_row["total_revenue"] += part_timers_revenue_per_period
			rev_data.append(part_timers_row)	
				
		elif row.name != 'PROJ-0018': #ignoring Elite HQ
			# Fetch employees according to projects
			employees = frappe.get_all('Employee',
							  		filters={'project': row.name}, 
									fields=['name', 'employee_name','project','project_name','status','relieving_date','date_of_joining'])
			row["total_revenue"] = 0.0
			for period in period_list:
				emps_count = 0
				for emp in employees:
					if emp.status == "Active" and emp.date_of_joining >= period.from_date:
						emps_count += 1
					else:
						if emp.relieving_date and emp.relieving_date <= period.to_date:
							emps_count +=1
			
				row["no_of_emps"] = emps_count
				project_revenue_per_period = emps_count * row.erc_fee
				row[period.key] = project_revenue_per_period
				row["total_revenue"] += project_revenue_per_period
			row["erc_fee"] = frappe.utils.fmt_money(row.erc_fee, currency="", precision=2)
			rev_data.append(row)
	
	#Append Revenue row
	total_revenue = sum(row["total_revenue"] for row in rev_data)
	revenue_row = {"account": "Revenue","total": total_revenue, "indent": 0.0}
	for period in period_list:
		revenue_row[period.key] = sum(row[period.key] if row.get(period.key) else 0 for row in rev_data)
	full_data.append(revenue_row)
	#Append project wise breakdown under revenue
	for row in rev_data:
		projectwise_rows = {"account": row["project_name"] ,"total": row["total_revenue"] , "indent": 1.0}
		for period in period_list:
			projectwise_rows[period.key] = row[period.key] if row.get(period.key) else 0
		full_data.append(projectwise_rows)

	cogs_row = {"account": "COGS","total": 0}
	full_data.append(cogs_row)
	gross_row = {"account": '<strong>Gross Profit </strong>',"total": total_revenue}
	for period in period_list:
		gross_row[period.key] = sum(row[period.key] if row.get(period.key) else 0 for row in rev_data)
	full_data.append(gross_row)
	#empty row
	empty_row = {}
	full_data.append(empty_row)

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
	manpower_row = {"account": "G&A Manpower Expense","total": 0,  "indent": 0.0}
	full_data.append(manpower_row)
	
	#append those expense account that have expense category as Manpower Expense
	for acc_row in expense:
		if "account" in acc_row and frappe.db.exists("Account", {"name": acc_row["account"], "is_group": 0, "custom_expense_category": "Manpower Expense"}):
			account_wise_row = {"account": acc_row["account_name"] ,"total": acc_row["total"],  "indent": 1.0}
			for period in period_list:
				if acc_row[period.key]:
					account_wise_row[period.key] = acc_row[period.key]
			exp_data.append(account_wise_row)
		
	for period in period_list:
		manpower_row[period.key] = sum(row[period.key] if row.get(period.key) else 0 for row in exp_data)
	total_of_manpower_expense = manpower_row["total"] = sum(row["total"] for row in exp_data)

	#append exp_data in full_data
	full_data.extend(exp_data)

	#Other Expense BreakDown
	other_exp_row = {"account": "Other Expense","total":0,  "indent": 0.0}
	full_data.append(other_exp_row)
	
	#append those expense account that have expense category as Other Expense
	for acc_row in expense:
		if "account" in acc_row and frappe.db.exists("Account", {"name": acc_row["account"], "is_group": 0, "custom_expense_category": "Other Expense"}):
			account_wise_row = {"account": acc_row["account_name"] ,"total": acc_row["total"],  "indent": 1.0}
			for period in period_list:
				if acc_row[period.key]:
					account_wise_row[period.key] = acc_row[period.key]
			othr_exp_data.append(account_wise_row)
	for period in period_list:
		other_exp_row[period.key] = sum(row[period.key] if row.get(period.key) else 0 for row in othr_exp_data)
	total_of_other_expense = other_exp_row["total"] = sum(row["total"] for row in othr_exp_data)

	#append othr_exp_data in full_data
	full_data.extend(othr_exp_data)

	#append total expense row
	total_expense = total_of_manpower_expense + total_of_other_expense
	total_expense_row = {"account": '<strong>Total Expense </strong>',"total": total_expense}
	#extend exp_data with othr_expense to get total by month key
	exp_data.extend(othr_exp_data)
	for period in period_list:
		total_expense_row[period.key] = sum(row[period.key] if row.get(period.key) else 0 for row in exp_data)
	full_data.append(total_expense_row)
	#empty row
	full_data.append(empty_row)
	operating_profit = total_revenue - total_expense  
	operating_profit_row = {"account": '<strong>Operating Profit </strong>',"total": operating_profit}
	full_data.append(operating_profit_row)
	#empty row
	full_data.append(empty_row)
	income_loss_row = {"account": "Other income/loss","total": 0}
	full_data.append(income_loss_row)
	net_income_row = {"account": '<strong>Net Income - Monthly </strong>',"total": operating_profit}
	full_data.append(net_income_row)

	# Calculate the difference for each month
	difference = {}
	for key in gross_row.keys():
		if key != 'account' and key != 'total':
			difference[key] = gross_row[key] - total_expense_row[key]
	
	#Update the "Operating Profit" and "Net Incom - Monthly" row with the differences
	for key, value in difference.items():
		operating_profit_row[key] = value
		net_income_row[key] = value


	return full_data

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