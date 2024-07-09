import frappe

#Add project filter in the function of cord file
#Function Name: make_filters(self)
#Below is the New Funcation code

def make_filters(self):
	filters = frappe._dict()
	filters["company"] = self.company
	filters["branch"] = self.branch
	filters["department"] = self.department
	filters["designation"] = self.designation
	filters["project"] = self.projects

	return filters

#Add project error msg in the function of core file
#Function Name: fill_employee_details(self)
#Below is the new function code

@frappe.whitelist()
def fill_employee_details(self):
	self.set("employees", [])
	employees = self.get_emp_list()
	if not employees:
		error_msg = _(
			"No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>Payroll Payable Account: {2}"
		).format(
			frappe.bold(self.company),
			frappe.bold(self.currency),
			frappe.bold(self.payroll_payable_account),
		)
		if self.projects:
			error_msg += "<br>" + _("Project: {0}").format(frappe.bold(self.projects))
		if self.branch:
			error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
		if self.department:
			error_msg += "<br>" + _("Department: {0}").format(frappe.bold(self.department))
		if self.designation:
			error_msg += "<br>" + _("Designation: {0}").format(frappe.bold(self.designation))
		if self.start_date:
			error_msg += "<br>" + _("Start date: {0}").format(frappe.bold(self.start_date))
		if self.end_date:
			error_msg += "<br>" + _("End date: {0}").format(frappe.bold(self.end_date))
		frappe.throw(error_msg, title=_("No employees found"))

	for d in employees:
		self.append("employees", d)

	self.number_of_employees = len(self.employees)
	return self.get_employees_with_unmarked_attendance()

#Add project filter condition in the function of core file
#Function Name: get_filter_condition(filters) 
#Below is the new Function code

def get_filter_condition(filters):
	cond = ""
	for f in ["company", "branch", "department", "designation", "project"]:
		if filters.get(f):
			cond += " and t1." + f + " = " + frappe.db.escape(filters.get(f))

	return cond

