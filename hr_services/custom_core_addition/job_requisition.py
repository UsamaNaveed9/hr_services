import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import format_duration, get_link_to_form, time_diff_in_seconds
from frappe import _

#expected_compensation and description condition added into the validate_duplicates funciton
#also passed the salary in frappe throw.

def validate_duplicates(self):
		duplicate = frappe.db.exists(
			"Job Requisition",
			{
				"designation": self.designation,
				"department": self.department,
				"requested_by": self.requested_by,
				"status": ("not in", ["Cancelled", "Filled"]),
				"name": ("!=", self.name),
				"expected_compensation": self.expected_compensation,
				"description": self.description,
			},
		)

		if duplicate:
			frappe.throw(
				_("A Job Requisition for {0} requested by {1} with same salary {2} and description already exists: {3}").format(
					frappe.bold(self.designation),
					frappe.bold(self.requested_by),
					frappe.bold(self.expected_compensation),
					get_link_to_form("Job Requisition", duplicate),
				),
				title=_("Duplicate Job Requisition"),
			)

#Project and Project Name added in core file function
#Function Name: make_job_opening(source_name, target_doc=None)
#Below is the updated code

@frappe.whitelist()
def make_job_opening(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.job_title = source.designation
		target.status = "Open"
		target.currency = frappe.db.get_value("Company", source.company, "default_currency")
		target.lower_range = source.expected_compensation
		target.description = source.description
		target.project = source.requested_by
		target.project_name = source.requested_by_name

	return get_mapped_doc(
		"Job Requisition",
		source_name,
		{
			"Job Requisition": {
				"doctype": "Job Opening",
			},
			"field_map": {
				"designation": "designation",
				"name": "job_requisition",
				"department": "department",
				"no_of_positions": "vacancies",
				"requested_by": "project",
				"requested_by_name": "project_name",
			},
		},
		target_doc,
		set_missing_values,
	)