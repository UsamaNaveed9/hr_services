import frappe
from frappe import _
from frappe.model.document import Document


#updated line in the below functons are mentioned with '#this'
class EmployeeBoardingController(Document):
	def on_submit(self):
		# create the project for the given employee onboarding
		project_name = _(self.doctype) + " : "
		if self.doctype == "Employee Onboarding":
			project_name += self.job_applicant
		else:
			project_name += self.employee

		if self.doctype != "Employee Onboarding":  			#this to
			project = frappe.get_doc(
				{
					"doctype": "Project",
					"project_name": project_name,
					"expected_start_date": self.date_of_joining
					if self.doctype == "Employee Onboarding"
					else self.resignation_letter_date,
					"department": self.department,
					"company": self.company,
				}
			).insert(ignore_permissions=True, ignore_mandatory=True)
			self.db_set("project", project.name)			#this

		self.db_set("boarding_status", "Pending")
		self.reload()
		self.create_task_and_notify_user()
		
	def create_task_and_notify_user(self):
		# create the task for the given project and assign to the concerned person
		holiday_list = self.get_holiday_list()

		for activity in self.activities:
			if activity.task:
				continue

			dates = self.get_task_dates(activity, holiday_list)

			task = frappe.get_doc(
				{
					"doctype": "Task",
					"project": self.project,
					"job_applicant": self.job_applicant					#this
					if self.doctype == "Employee Onboarding"			#this
					else "",											#this
					"subject": activity.activity_name + " : " + self.employee_name,
					"description": activity.description,
					"department": self.department,
					"company": self.company,
					"task_weight": activity.task_weight,
					"exp_start_date": dates[0],
					"exp_end_date": dates[1],
				}
			).insert(ignore_permissions=True)
			activity.db_set("task", task.name)

			users = [activity.user] if activity.user else []
			if activity.role:
				user_list = frappe.db.sql_list(
					"""
					SELECT
						DISTINCT(has_role.parent)
					FROM
						`tabHas Role` has_role
							LEFT JOIN `tabUser` user
								ON has_role.parent = user.name
					WHERE
						has_role.parenttype = 'User'
							AND user.enabled = 1
							AND has_role.role = %s
				""",
					activity.role,
				)
				users = unique(users + user_list)

				if "Administrator" in users:
					users.remove("Administrator")

			# assign the task the users
			if users:
				self.assign_task_to_users(task, users)

	def on_cancel(self):
		# delete task project
		project = self.project
		if self.doctype == "Employee Onboarding":									#this to till end
			job_applicant = self.job_applicant
			for task in frappe.get_all("Task", filters={"job_applicant": job_applicant}):
				frappe.delete_doc("Task", task.name, force=1)
			for activity in self.activities:
				activity.db_set("task", "")

			frappe.msgprint(
				_("Linked Tasks deleted."), alert=True, indicator="blue"
			)
		else:
			for task in frappe.get_all("Task", filters={"project": project}):
				frappe.delete_doc("Task", task.name, force=1)
			frappe.delete_doc("Project", project, force=1)
			self.db_set("project", "")
			for activity in self.activities:
				activity.db_set("task", "")

			frappe.msgprint(
				_("Linked Project {} and Tasks deleted.").format(project), alert=True, indicator="blue"
			)			    