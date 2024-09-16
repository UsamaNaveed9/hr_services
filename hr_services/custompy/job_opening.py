# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_job_applicant(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.status = "Accepted"

	doc = get_mapped_doc(
		"Job Opening",
		source_name,
		{
			"Job Opening": {
				"doctype": "Job Applicant",
				"field_map": {"name": "job_title",
				  			"requested_by": "project",
							"requested_by_name": "project_name",
							"custom_divisions": "custom_divisions",
							"designation": "designation",
							"currency": "currency",
							"lower_range": "lower_range",
						},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc