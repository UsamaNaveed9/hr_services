# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta
from erpnext.accounts.utils import get_balance_on
from frappe import _

class AccruedEndofServices(Document):
	def before_submit(self):
		if self.accrued_end_of_services_for == "Clients-Emp":
			acc_name = "2230109-01 - Accrued ESB - Operations - ERC"
			acc_bal = get_balance_on(account=acc_name, date=self.me_date)
			if acc_bal < 0:
				acc_bal = -1 * acc_bal

			if self.total_accrued > acc_bal:
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Journal Entry"
				jv.company = "Elite Resources Center"
				jv.posting_date = self.me_date
				
				jv_row1 = frappe.new_doc("Journal Entry Account")
				jv_row1.account = "51-0112 - OPE-ME- ESB - ERC"
				jv_row1.debit_in_account_currency = self.total_accrued - acc_bal
				jv_row1.credit_in_account_currency = 0
				jv.append("accounts", jv_row1)

				jv_row2 = frappe.new_doc("Journal Entry Account")
				jv_row2.account = "2230109-01 - Accrued ESB - Operations - ERC"
				jv_row2.debit_in_account_currency = 0
				jv_row2.credit_in_account_currency = self.total_accrued - acc_bal
				jv.append("accounts", jv_row2)

				jv.user_remark = f"Accrued End of Services of {self.month_name} for Clients"
				jv.custom_accrued_end_of_services = self.name
				jv.save()
				jv.submit()
			else:
				frappe.throw(_(f"Account: {acc_name} Balance is Greater than Total Accrued End of Services"))

		elif self.accrued_end_of_services_for == "Elite-HQ-Emp":
			acc_name = "2230109-02 - Accrued ESB - G&A - ERC"
			acc_bal = get_balance_on(account=acc_name, date=self.me_date)
			if acc_bal < 0:
				acc_bal = -1 * acc_bal

			if self.total_accrued > acc_bal:
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Journal Entry"
				jv.company = "Elite Resources Center"
				jv.posting_date = self.me_date
				
				jv_row1 = frappe.new_doc("Journal Entry Account")
				jv_row1.account = "52-0112 - G&A-ME- ESB - ERC"
				jv_row1.debit_in_account_currency = self.total_accrued - acc_bal
				jv_row1.credit_in_account_currency = 0
				jv.append("accounts", jv_row1)

				jv_row2 = frappe.new_doc("Journal Entry Account")
				jv_row2.account = "2230109-02 - Accrued ESB - G&A - ERC"
				jv_row2.debit_in_account_currency = 0
				jv_row2.credit_in_account_currency = self.total_accrued - acc_bal
				jv.append("accounts", jv_row2)

				jv.user_remark = f"Accrued End of Services of {self.month_name} for Elite HQ"
				jv.custom_accrued_end_of_services = self.name
				jv.save()
				jv.submit()
			else:
				frappe.throw(_(f"Account: {acc_name} Balance is Greater than Total End of Services"))	

@frappe.whitelist()
def calculate_accrued_end_of_services(end_date,emp_of):
	#get all employess without alhokair id PROJ-0007, Elite HQ id PROJ-0018, AP - Abdullah Hashim id PROJ-0021 employees
	if emp_of == "Clients-Emp":
		excluded_projects = ['PROJ-0007', 'PROJ-0018', 'PROJ-0021']
		employees = frappe.get_all('Employee', 
								filters={
									'status': 'Active',
									'project': ('not in', excluded_projects)
									}, 
								fields= ['name','employee_name','date_of_joining','project','project_name','basic_salary',
											'housing_allowance','transport_allowance','food_allowance','mobile_allowance','ctc'])
		#frappe.errprint(employees)
	#only elite hq employees	
	elif emp_of == "Elite-HQ-Emp":
		employees = frappe.get_all('Employee', 
								filters={
									'status': 'Active',
									'project': 'PROJ-0018'
									}, 
								fields= ['name','employee_name','date_of_joining','project','project_name','basic_salary',
											'housing_allowance','transport_allowance','food_allowance','mobile_allowance','ctc'])
		#frappe.errprint(employees)

	for emp in employees:
		#getting differenc between end of month data and date of joining of an employee spent time in a company. years(how many years),months,days and diff_in_years(total)
		diff = get_diff(emp.date_of_joining,end_date)
		accrued_eos_amt = 0
		yrs = diff['diff_in_years']
		#total salary without mobile allowance(mb_allwn)
		sl = emp.basic_salary + emp.housing_allowance + emp.transport_allowance + emp.food_allowance
		if yrs > 5:
			accrued_eos_amt = (sl / 2) * 5
			rm_years = yrs - 5
			accrued_eos_amt = accrued_eos_amt + (sl * rm_years)
		else:
			accrued_eos_amt = (sl / 2) * yrs

		emp['years'] = diff['years']
		emp['months'] = diff['months']
		emp['days'] = diff['days']
		emp['diff_in_years'] = diff['diff_in_years']
		emp['accrued_end_of_services'] = accrued_eos_amt
	
	return employees

@frappe.whitelist()
def get_diff(startdate,lastdate):
	result = {}
	#startdate is the date of joining of employee and lastdate is the month end date of record
	start_date = startdate
	end_date = datetime.strptime(lastdate, '%Y-%m-%d')

    # Calculate the difference of two dates
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

	result['years'] = years
	result['months'] = months
	result['days'] = days
	result['diff_in_years'] = difference_in_years

	return result