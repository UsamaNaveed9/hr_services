# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import copy

def execute(filters=None):
	columns = get_columns(filters)
	data = get_cost_sheet_details(filters)
	return columns, data

def get_columns(filters):
	if filters.get("sheet_type") == "Cenomi":
		columns = [
			{"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
			{"label": _("Iqama/ID"), "fieldname": "id_or_iqama", "fieldtype": "Data", "width": 110},
			{"label": _("Nationality"), "fieldname": "nationality", "fieldtype": "Data", "width": 110},
			{"label": _("Job Title"), "fieldname": "job_title", "fieldtype": "Data", "width": 140},
		]

		field_label_mapping = {
			"basic": "Basic",
			"housing": "Housing",
			"transport": "Transport",
			"mobile": "Mobile",
			"gasoline": "Gasoline",
			"food": "Food",
			"total_salary": "Total Salary",
			"gosi": "GOSI",
			"end_of_services": "End of Services",
			"monthly_transfer_fee": "Transfer Fee",
			"insurance_class": "Insurance Class",
			"monthly_med_inc": "Medical Insurance",
			"leave_amt_per_month": "Annual Leave",
			"exit_re_entry_monthly": "Exit Re-Entry",
			"ticket_amount_monthly": "Ticket",
			"monthly_iqama_fee": "Iqama Fee",
			"monthly_wl_fee": "Working License Fee",
			"transaction_fee": "Transaction Fee",
			"oh_cost_total": "OH Cost Total",
			"erc_fee": "ERC Fee",
			"total_with_erc": "Total including ERC Fee",
			"total_cost": "Total Cost"
		}

		columns.extend([
			{
				"label": field_label_mapping[field],
				"fieldname": field,
				"fieldtype": "Currency" if field != "insurance_class" else "Data",
				"options": "currency",
				"width": 120
			} for field in field_label_mapping
		])	
	elif filters.get("sheet_type") == "ACWA":
		columns = [
			{"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
			{"label": _("Iqama/ID"), "fieldname": "id_or_iqama", "fieldtype": "Data", "width": 110},
			{"label": _("Nationality"), "fieldname": "nationality", "fieldtype": "Data", "width": 110},
			{"label": _("Job Title"), "fieldname": "job_title", "fieldtype": "Data", "width": 140},
		]

		field_label_mapping = {
			"basic": "Basic",
			"housing": "Housing",
			"transport": "Transport",
			"mobile": "Mobile",
			"vt_allowance": "Vacation Travel Allowance",
			"neom_allowance": "NEOM Allowance",
			"gosi": "GOSI",
			"total_salary_monthly": "TOTAL SALARY EXP -MONTHLY",
			"insurance_class": "Insurance Class",
			"yearly_med_inc": "Medical Insurance",
			"wl_fee": "Working License",
			"iqama_fee": "Iqama Renewal",
			"ticket_amount": "Ticket",
			"exit_re_entry": "Exit Re-Entry",
			"total_yearly_cost": "TOTAL YEARLY COST OTHER THAN SALARY",
			"transfer_fee": "Transfer Fee",
			"relocation_allowance": "Relocation Allowance",
			"recruitment_cost": "Recruitment Cost",
			"total_one_time_cost": "TOTAL ONE TIME COST",
			"erc_fee": "ERC FEE YEARLY",
			"total_cost_per_year": "TOTAL COST PER YEAR",
			"vat": "Vat 15%"
		}

		columns.extend([
			{
				"label": field_label_mapping[field],
				"fieldname": field,
				"fieldtype": "Currency" if field != "insurance_class" else "Data",
				"options": "currency",
				"width": 120
			} for field in field_label_mapping
		])
	elif filters.get("sheet_type") == "Misk" and filters.get("emp_type") == "Full Time":
		columns = [
			{"label": _("Name"), "fieldname": "employee_name_m", "fieldtype": "Data", "width": 200},
			{"label": _("Nationality"), "fieldname": "nationality_m", "fieldtype": "Data", "width": 110},
			{"label": _("Job Title"), "fieldname": "designation_m", "fieldtype": "Data", "width": 140},
		]

		field_label_mapping = {
			"basic_pm": "Basic Salary",
			"housing_pm": "Housing",
			"transportation_pm": "Transportation",
			"mi_pm": "MI-Emp",
			"spouse_pm": "MI-Spouse",
			"no_of_children_m": "No of Children",
			"childs_pm": "MI-# of Children",
			"transfer_fee_pm": "Iqama Transfer Fee",
			"iqama_fee_pm": "Iqama Fee",
			"labor_pm": "Labor Card",
			"wl_fee_pm": "Working Liecence Fee",
			"st_fee_pm": "Salary Transfer Fees",
			"gosi_pm": "GOSI",
			"eos_pm": "EOS",
			"annual_leave_pm": "Annual Leave",
			"agency_fee_pm": "Agencey Fees 8%",
		}

		columns.extend([
			{
				"label": field_label_mapping[field],
				"fieldname": field,
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120
			} for field in field_label_mapping
		])
	elif filters.get("sheet_type") == "Misk" and filters.get("emp_type") == "Part Time":
		columns = [
			{"label": _("Name"), "fieldname": "employee_name_m", "fieldtype": "Data", "width": 420},
			{"label": _("Nationality"), "fieldname": "nationality_m", "fieldtype": "Data", "width": 110},
			{"label": _("Job Title"), "fieldname": "designation_m", "fieldtype": "Data", "width": 140},
		]

		field_label_mapping = {
			"daily_rate": "Daily Rate",
			"salary_transfer_fee": "Salary transfer fees",
			"agency_fee": "Agencey Fees 8%",
			"total_daily_rate": "Total Daily Rate"
		}

		columns.extend([
			{
				"label": field_label_mapping[field],
				"fieldname": field,
				"fieldtype": "Data",
				"width": 120
			} for field in field_label_mapping
		])		

	return columns

def calculate_total(data, field):
	return sum(row[field] for row in data)

def get_cost_sheet_details(filters):
	filter_obj = {
		"posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
	}

	if filters.get("sheet_type") == "Cenomi":
		filter_obj.update({"sheet_type": filters.get("sheet_type")})

		cost_details = frappe.get_all(
			"Costing Sheet",
			fields=[
				"employee_name", "id_or_iqama", "nationality", "job_title",
				"basic", "housing", "transport", "mobile", "gasoline", "food",
				"total_salary", "gosi", "end_of_services", "monthly_transfer_fee",
				"insurance_class", "monthly_med_inc", "leave_amt_per_month",
				"exit_re_entry_monthly", "ticket_amount_monthly", "monthly_iqama_fee",
				"monthly_wl_fee", "transaction_fee", "oh_cost_total", "erc_fee",
				"total_with_erc", "total_cost"
			],
			filters=filter_obj,
		)
		
		total_fields = [
			"basic", "housing", "transport", "mobile", "gasoline", "food",
			"total_salary", "gosi", "end_of_services", "monthly_transfer_fee",
			"monthly_med_inc", "leave_amt_per_month", "exit_re_entry_monthly",
			"ticket_amount_monthly", "monthly_iqama_fee", "monthly_wl_fee",
			"transaction_fee", "oh_cost_total", "erc_fee", "total_with_erc", "total_cost"
		]

		row_monthly = {
			"employee_name": "",
			"id_or_iqama": "",
			"nationality": "",
			"job_title": '<strong>Total P/M</strong>',
			**{field: calculate_total(cost_details, field) for field in total_fields},
		}

		monthly_total = {field: calculate_total(cost_details, field) for field in total_fields}

		cost_details.append(row_monthly)

		row_yearly = {
			"employee_name": "",
			"id_or_iqama": "",
			"nationality": "",
			"job_title": '<strong>Total P/A</strong>',
			**{field: monthly_total[field] * 12 for field in total_fields},
		}
		
		cost_details.append(row_yearly)

		return cost_details
	
	elif filters.get("sheet_type") == "ACWA":
		filter_obj.update({"sheet_type": filters.get("sheet_type")})

		cost_details = frappe.get_all(
			"Costing Sheet",
			fields=[
				"employee_name", "id_or_iqama", "nationality", "job_title", "insurance_class",
				"basic", "housing", "transport", "mobile", "vt_allowance", "neom_allowance", "gosi", 
				"yearly_med_inc", "wl_fee","iqama_fee","ticket_amount","exit_re_entry",
				"transfer_fee","relocation_allowance","recruitment_cost","erc_fee"
			],
			filters=filter_obj,
		)
		
		for row in cost_details:
			row["total_salary_monthly"] = row.basic + row.housing + row.transport + row.mobile + row.vt_allowance + row.neom_allowance + row.gosi
			row["total_yearly_cost"] = row.yearly_med_inc + row.wl_fee + row.iqama_fee + row.ticket_amount + row.exit_re_entry
			row["total_one_time_cost"] = row.transfer_fee + row.relocation_allowance + row.recruitment_cost
			row["total_cost_per_year"] = (row.total_salary_monthly * 12) + row.total_yearly_cost + row.total_one_time_cost + row.erc_fee
			row["vat"] = row.total_cost_per_year * 0.15
 		
		return cost_details
	
	elif filters.get("sheet_type") == "Misk" and filters.get("emp_type") == "Full Time":
		filter_obj.update({"sheet_type": filters.get("sheet_type")})
		filter_obj.update({"employment_type": filters.get("emp_type")})

		cost_details = frappe.get_all(
			"Costing Sheet",
			fields=[
				"employee_name_m", "nationality_m", "designation_m", "basic_pm","housing_pm",
				"transportation_pm","mi_pm","spouse_pm","no_of_children_m","childs_pm","transfer_fee_pm",
				"iqama_fee_pm","labor_pm","wl_fee_pm","st_fee_pm","gosi_pm","eos_pm","annual_leave_pm","agency_fee_pm"
			],
			filters=filter_obj,
		)
 		
		return cost_details
	
	elif filters.get("sheet_type") == "Misk" and filters.get("emp_type") == "Part Time":
		filter_obj.update({"sheet_type": filters.get("sheet_type")})
		filter_obj.update({"employment_type": filters.get("emp_type")})

		cost_details_data = frappe.get_all(
			"Costing Sheet",
			fields=[
				"employee_name_m", "nationality_m", "designation_m", "monthly_pkg_amt", "daily_rate",
				"salary_transfer_fee", "agency_fee", "total_daily_rate"
			],
			filters=filter_obj,
		)
		for cdd in cost_details_data:
			# Format numeric values as currency
			for key, value in cdd.items():
				if isinstance(value, (int, float)):
					cdd[key] = frappe.utils.fmt_money(value, currency="", precision=2)


		cost_details = copy.deepcopy(cost_details_data)
		# Append an empty row
		cost_details.append({})

		# Append a row with employee_name_m = "Keywords Guide"
		cost_details.append({
			"employee_name_m": "Keywords Guide"
		})
		# Append an empty row
		cost_details.append({})

		cost_details.append({
			"employee_name_m": "1. Salary Tranfer will be Charged as per the bank"
		})

		cost_details.append({
			"employee_name_m": "2. Mentioned Salary Transfer Fee Cost is Per Transaction."
		})
		# Append an empty row
		cost_details.append({})
		for row in cost_details_data:
			msg = f"{row.monthly_pkg_amt} Monthly/30 days = {row.daily_rate} SAR"
			cost_details.append({
				"employee_name_m": msg
			})
 		
		return cost_details
