#Copyright (c) 2023, Elite Resources and contributors
#For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
import json

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.personal_email, target.first_name = frappe.db.get_value(
			"Job Applicant", source.job_applicant, ["email_id", "applicant_name"]
		)
		source_doc = frappe.get_doc("Job Offer",source_name)
		others = 0
		for sd in source_doc.custom_salary_details:
			if sd.salary_components == "Basic Salary":
				target.basic_salary = sd.amount
			elif sd.salary_components == "Housing Allowance":
				target.housing_allowance = sd.amount
			elif sd.salary_components == "Transportations Allowance":
				target.transport_allowance = sd.amount
			else:
				others += sd.amount
		target.food_allowance = others
		target.ctc = source_doc.custom_total_salary
	doc = get_mapped_doc(
		"Job Offer",
		source_name,
		{
			"Job Offer": {
				"doctype": "Employee",
				"field_map": {"applicant_name": "employee_name",
				  			"custom_applicant_name_in_arabic": "name_in_arabic",
							"offer_date": "scheduled_confirmation_date",
							"custom_project": "project",
							"custom_salutation": "salutation",
							"custom_country": "nationality"},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc


@frappe.whitelist()
def make_contract(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.party_type = "Job Applicant"
		if source.custom_contract_duration == "1 Year":
			target.custom_contract_duration = 1
		elif source.custom_contract_duration == "2 Year":
			target.custom_contract_duration = 2

	doc = get_mapped_doc(
		"Job Offer",
		source_name,
		{
			"Job Offer": {
				"doctype": "Contract",
				"field_map": {"name": "custom_job_offer",
							"job_applicant": "party_name",
							"applicant_name": "custom_c_name",
							"custom_applicant_name_in_arabic": "custom_name_in_arabic",
							"custom_country": "custom_nationality",
							"designation": "custom_designation",
							"custom_contract_type": "custom_contract_type"
				},
			},
			"Contract Details": {"doctype": "Contract Details"},
		},
		target_doc,
		set_missing_values,
	)
	return doc


@frappe.whitelist()
def get_terms_and_conditions(template_name, doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	terms_and_conditions = frappe.get_doc("Terms and Conditions", template_name)

	if terms_and_conditions.custom_terms_and_conditions_in_arabic:
		return frappe.render_template(terms_and_conditions.custom_terms_and_conditions_in_arabic, doc)
