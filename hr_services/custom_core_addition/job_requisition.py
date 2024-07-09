import frappe
from frappe.model.mapper import get_mapped_doc


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