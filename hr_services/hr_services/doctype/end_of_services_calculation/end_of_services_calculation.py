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
	days = delta.days + 1

	difference_in_years = -((start_date - end_date).days / 365.25)  # Using 365.25 to account for leap years

	# Round the value to 2 decimal places
	rounded_diff_year = round(difference_in_years, 2)
	result.append(years)
	result.append(months)
	result.append(days)
	result.append(rounded_diff_year)

	return result

@frappe.whitelist()
def calculate_eos(reason,salary,years):
	if reason == "Termination":
		eos_amt = 0
		yrs = float(years)
		sl = float(salary)
		if yrs > 5:
			eos_amt = (sl / 2) * 5
			rm_years = yrs - 5
			eos_amt = eos_amt + (sl * rm_years)
		else:
			eos_amt = (sl / 2) * yrs	

	return eos_amt	

