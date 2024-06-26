# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from hijri_converter import Hijri, Gregorian
from datetime import datetime

@frappe.whitelist()
def update_salary(doc, method):
	 # List of fields to check for changes
	fields_to_check = ["basic_salary", "housing_allowance", "transport_allowance", "food_allowance", "mobile_allowance"]
	
	# Flag to check if any relevant field has changed
	relevant_field_changed = any(doc.has_value_changed(field) for field in fields_to_check)

	if relevant_field_changed:
		# Fetch the salary structure assignment in one query
		struct_assigned = frappe.db.get_value(
			"Salary Structure Assignment", 
			{"employee": doc.name, "project": doc.project, "company": doc.company}, 
			["name", "base", "housing_allowance", "transport_allowance", "food_allowance", "mobile_allowance"],
			as_dict=True
		)

		if struct_assigned:
			updates = {}
			if struct_assigned['base'] != doc.basic_salary:
				updates["base"] = doc.basic_salary
			if struct_assigned['housing_allowance'] != doc.housing_allowance:
				updates["housing_allowance"] = doc.housing_allowance
			if struct_assigned['transport_allowance'] != doc.transport_allowance:
				updates["transport_allowance"] = doc.transport_allowance
			if struct_assigned['food_allowance'] != doc.food_allowance:
				updates["food_allowance"] = doc.food_allowance
			if struct_assigned['mobile_allowance'] != doc.mobile_allowance:
				updates["mobile_allowance"] = doc.mobile_allowance

			if updates:
				# Perform a single update query with the collected updates
				frappe.db.set_value("Salary Structure Assignment", struct_assigned['name'], updates, update_modified=False)
				frappe.db.commit()

	if doc.iqama_national_id and frappe.db.exists("Employee",{"iqama_national_id": doc.iqama_national_id, "name": ["!=", doc.name]}):
		frappe.throw(_("Iqama No/National ID must be Unique. This <b>{0}</b> is already assigned to another Employee").format(doc.iqama_national_id))	

@frappe.whitelist()
def check_id(doc, method):
	if doc.iqama_national_id and frappe.db.exists("Employee",{"iqama_national_id": doc.iqama_national_id}):
		frappe.throw(_("Iqama No/National ID must be Unique. This <b>{0}</b> is already assigned to another Employee").format(doc.iqama_national_id))

@frappe.whitelist()
def convert_into_hijri(date):
	hijri_date = Gregorian.fromisoformat(date).to_hijri().isoformat()
	# Parse the date
	parsed_date = datetime.strptime(hijri_date, "%Y-%m-%d")

	# Format the date to "DD-MM-YYYY"
	formatted_date = parsed_date.strftime("%d-%m-%Y")
	
	return formatted_date

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_classes(doctype, txt, searchfield, start, page_len, filters):
	project = [filters.get("value")]
	if not project:
		frappe.throw(_("Project value is required"))

	return frappe.get_all(
		"Health Insurances",
		filters={"parent": ("in", project)},
		fields=["distinct insurance"],
		as_list=1,
	)

	
