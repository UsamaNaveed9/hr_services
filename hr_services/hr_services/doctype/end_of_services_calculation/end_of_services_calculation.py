# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta

class EndofServicesCalculation(Document):
	pass

@frappe.whitelist()
def get_diff(startdate,lastdate):
	result = []
	start_date = datetime.strptime(startdate, '%Y-%m-%d')
	end_date = datetime.strptime(lastdate, '%Y-%m-%d')

    # Calculate the difference
	delta = relativedelta(end_date, start_date)
	years = delta.years
	months = delta.months
	days = delta.days
	if days > 29:
		months = months + 1
		days = 0
	if months > 11:
		years = years + 1
		months = 0


	difference_in_years = years + (months / 12) + (days / 360)

	result.append(years)
	result.append(months)
	result.append(days)
	result.append(difference_in_years)

	return result

@frappe.whitelist()
def calculate_eos(reason,salary,diff_yrs):
	if reason == "Termination" or reason == "Resignation at Contract Completion":
		eos_amt = 0
		yrs = float(diff_yrs)
		sl = float(salary)
		if yrs > 5:
			eos_amt = (sl / 2) * 5
			rm_years = yrs - 5
			eos_amt = eos_amt + (sl * rm_years)
		else:
			eos_amt = (sl / 2) * yrs
	elif reason == "Resignation":
		eos_amt = 0
		yrs = float(diff_yrs)
		sl = float(salary)
		if yrs < 2:
			eos_amt = 0
		elif yrs > 2 and yrs < 5:
			eos_amt = (sl / 2) * 1/3 * yrs
		elif yrs > 5 and yrs < 10:
			eos_amt = (sl / 2) * 2/3 * 5
			rm_yrs = yrs - 5
			eos_amt = eos_amt + (sl * 2/3 * rm_yrs)
		elif yrs > 10:
			eos_amt = (sl / 2) * 5
			rm_yrs = yrs - 5
			eos_amt = eos_amt + (sl * rm_yrs)

	return eos_amt