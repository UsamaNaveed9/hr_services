# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AccruedVacation(Document):
	pass

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
		if allocation:
			taken_leaves = get_taken_leaves(emp.name,end_date,allocation.leave_type)
			leave_balance = (
				allocation.total_leaves_allocated
				- allocation.carry_forwarded_leaves_count
				- taken_leaves
			)
		
		emp['leave_balance'] = leave_balance
		#check if project is Arabian center (id PROJ-0017) then calculate on basic salary
		if emp.project == "PROJ-0017":
			emp['accrued_vacation_salary'] = (emp.basic_salary / 30 ) * leave_balance
		else:
			emp['accrued_vacation_salary'] = (emp.ctc / 30 ) * leave_balance

	frappe.errprint(employees)

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
				LeaveAllocation.total_leaves_allocated,
				LeaveAllocation.carry_forwarded_leaves_count,
			)
			.where(
				((LeaveAllocation.from_date <= date) & (date <= LeaveAllocation.to_date))
				& (LeaveAllocation.docstatus == 1)
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