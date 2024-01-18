# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from erpnext.accounts.utils import get_balance_on
from frappe import _

class AccruedVacation(Document):
	def before_submit(self):
		if self.accrued_salary_for == "Clients-Emp":
			acc_name = "2230108-01 - Accrued Vacation - Operations - ERC"
			acc_bal = get_balance_on(account=acc_name, date=self.me_date)
			if acc_bal < 0:
				acc_bal = -1 * acc_bal

			if self.total_accrued > acc_bal:
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Journal Entry"
				jv.company = "Elite Resources Center"
				jv.posting_date = self.me_date
				
				jv_row1 = frappe.new_doc("Journal Entry Account")
				jv_row1.account = "51-0115-01 - OPE-ME-VE- Salary - ERC"
				jv_row1.debit_in_account_currency = self.total_accrued - acc_bal
				jv_row1.credit_in_account_currency = 0
				jv.append("accounts", jv_row1)

				jv_row2 = frappe.new_doc("Journal Entry Account")
				jv_row2.account = "2230108-01 - Accrued Vacation - Operations - ERC"
				jv_row2.debit_in_account_currency = 0
				jv_row2.credit_in_account_currency = self.total_accrued - acc_bal
				jv.append("accounts", jv_row2)

				jv.user_remark = f"Accrued Vacation Salary of {self.month_name} for Clients"
				jv.accrued_vacation = self.name
				jv.save()
				jv.submit()
			else:
				frappe.throw(_(f"Account {acc_name}Balance is Greater than Total Accrued Vacation Salary"))

		elif self.accrued_salary_for == "Elite-HQ-Emp":
			acc_name = "2230108-02 - Accrued Vacation - G&A - ERC"
			acc_bal = get_balance_on(account=acc_name, date=self.me_date)
			if acc_bal < 0:
				acc_bal = -1 * acc_bal

			if self.total_accrued > acc_bal:
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Journal Entry"
				jv.company = "Elite Resources Center"
				jv.posting_date = self.me_date
				
				jv_row1 = frappe.new_doc("Journal Entry Account")
				jv_row1.account = "52-0115-01 - G&A-ME-VE- Salary - ERC"
				jv_row1.debit_in_account_currency = self.total_accrued - acc_bal
				jv_row1.credit_in_account_currency = 0
				jv.append("accounts", jv_row1)

				jv_row2 = frappe.new_doc("Journal Entry Account")
				jv_row2.account = "2230108-02 - Accrued Vacation - G&A - ERC"
				jv_row2.debit_in_account_currency = 0
				jv_row2.credit_in_account_currency = self.total_accrued - acc_bal
				jv.append("accounts", jv_row2)

				jv.user_remark = f"Accrued Vacation Salary of {self.month_name} for Elite HQ"
				jv.accrued_vacation = self.name
				jv.save()
				jv.submit()
			else:
				frappe.throw(_(f"Account: {acc_name} Balance is Greater than Total Accrued Vacation Salary"))	

@frappe.whitelist()
def calculate_accrued_salary(end_date,emp_of):
	#alhokair id PROJ-0007, Elite HQ id PROJ-0018, AP - Abdullah Hashim id PROJ-0021
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
		allocation = get_leave_allocation(emp.name,end_date)
		leave_balance = 0
		leaves_till_now = 0
		allocated_leaves = 0
		taken_leaves = 0
		till_date = datetime.strptime(end_date, '%Y-%m-%d').date()
		diff_days = (till_date - emp.date_of_joining).days
		#frappe.errprint(diff_days)
		#frappe.errprint(allocation.new_leaves_allocated)
		if allocation:
			allocated_leaves = allocation.new_leaves_allocated
			taken_leaves = get_taken_leaves(emp.name,end_date,allocation.leave_type)
			leaves_till_now = round((allocation.new_leaves_allocated / 365 ) * diff_days)
			leave_balance = (
				leaves_till_now - taken_leaves
			)
		
		emp['diff_days'] = diff_days
		emp['allocated_leaves'] = allocated_leaves
		emp['leaves_till_now'] = leaves_till_now
		emp['taken_leaves'] = taken_leaves
		emp['leave_balance'] = round(leave_balance)

		#check if project is Arabian center (id PROJ-0017) then calculate on basic salary
		if emp.project == "PROJ-0017":
			emp['accrued_vacation_salary'] = (emp.basic_salary / 30 ) * leave_balance
		else:
			#total salary without mobile allowance(mb_allwn)
			ctc_without_mb_allwn = emp.basic_salary + emp.housing_allowance + emp.transport_allowance + emp.food_allowance
			emp['accrued_vacation_salary'] = (ctc_without_mb_allwn / 30 ) * leave_balance
	
	return employees

@frappe.whitelist()
def get_leave_allocation(emp,end_date):
		date = end_date

		LeaveAllocation = frappe.qb.DocType("Leave Allocation")
		leave_allocation = (
			frappe.qb.from_(LeaveAllocation)
			.select(
				LeaveAllocation.name,
				LeaveAllocation.from_date,
				LeaveAllocation.leave_type,
				LeaveAllocation.to_date,
				LeaveAllocation.new_leaves_allocated,
			)
			.where(
				(LeaveAllocation.docstatus == 1)
				& (LeaveAllocation.leave_type == 'Annual Leave')
				& (LeaveAllocation.employee == emp)
			)
		).run(as_dict=True)
		
		return leave_allocation[0] if leave_allocation else None

@frappe.whitelist()
def get_taken_leaves(employee_id, end_date, leave_type):
	# Query to get taken leaves till a specific date
	query = """
		SELECT
			SUM(
				CASE
					WHEN from_date <= %(end_date)s AND to_date >= %(end_date)s THEN DATEDIFF(%(end_date)s, from_date) + 1
					WHEN from_date <= %(end_date)s AND to_date < %(end_date)s THEN DATEDIFF(to_date, from_date) + 1
					ELSE 0
				END
			) as total_taken_leaves
		FROM
			`tabLeave Application`
		WHERE
			employee = %(employee_id)s
			AND leave_type = %(leave_type)s
			AND from_date <= %(end_date)s
			AND status = 'Approved'
	"""

	# Parameters for the query
	params = {
		'employee_id': employee_id,
		'leave_type': leave_type,
		'end_date': end_date
	}

	# Execute the query
	result = frappe.db.sql(query, params, as_dict=True)

	# Extract the total taken leaves
	total_taken_leaves = result[0]['total_taken_leaves'] if result and result[0] else 0
	if not total_taken_leaves:
		total_taken_leaves = 0

	return total_taken_leaves