# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"label": _("Particulars"), "fieldname": "particulars", "fieldtype": "Data", "width": 400},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
	]
	
	return columns

def get_data(filters):
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
	
	total_row = {
		"project_name": '<strong>Total </strong>',
		"no_of_emps": sum(row["no_of_emps"] for row in data),
		"erc_fee": "",
		"total_revenue": sum(row["total_revenue"] for row in data)
	}
	#Append Revenue row
	total_revenue = sum(row["total_revenue"] for row in data)
	revenue_row = {"particulars": "Revenue","amount": total_revenue}
	mis_data.append(revenue_row)
	cogs_row = {"particulars": "COGS","amount": 0}
	mis_data.append(cogs_row)
	gross_row = {"particulars": '<strong>Gross Profit </strong>',"amount": total_revenue}
	mis_data.append(gross_row)
	
	data.append(total_row)

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