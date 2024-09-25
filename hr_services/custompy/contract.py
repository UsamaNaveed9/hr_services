# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from six import BytesIO
from docxtpl import DocxTemplate
import datetime
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def check_job_offer(doc, method):
	job_offer_salary = frappe.db.get_value("Job Offer",doc.custom_job_offer,"custom_total_salary")
	if doc.party_type == "Job Applicant":
		if frappe.db.exists("Contract",{"custom_job_offer": doc.custom_job_offer}):
			frappe.throw(_("Contract on this Job Offer <b>{0}</b> already exist").format(doc.custom_job_offer))
		elif job_offer_salary != doc.custom_total_salary:
			frappe.throw(_("Contract Total Salary: <b>{0}</b> must be equal to Job Offer Salary: <b>{1}</b>").format(doc.custom_total_salary,job_offer_salary))

@frappe.whitelist()
def validate_after_save(doc, method):
	job_offer_salary = frappe.db.get_value("Job Offer",doc.custom_job_offer,"custom_total_salary")
	if doc.docstatus == 0 and doc.party_type == "Job Applicant":
		if frappe.db.exists("Contract",{"custom_job_offer": doc.custom_job_offer,"name": ["!=", doc.name]}):
			frappe.throw(_("Contract on this Job Offer <b>{0}</b> already exist").format(doc.custom_job_offer))
		elif job_offer_salary != doc.custom_total_salary:
			frappe.throw(_("Contract Total Salary: <b>{0}</b> must be equal to Job Offer Salary: <b>{1}</b>").format(doc.custom_total_salary,job_offer_salary))

def _fill_template(template, data):
	"""
	Fill a word template with data.

	Makes use of BytesIO to write the resulting file to memory instead of disk.

	:param template:    path to docx file or file-like object
	:param data:    dict with keys and values
	"""
	doc = DocxTemplate(template)
	doc.render(data)
	_file = BytesIO()
	doc.docx.save(_file)
	return _file

@frappe.whitelist()
def fill_and_attach_template(doctype, name, template):
	"""
	Use a documents data to fill a docx template and attach the result.

	Reads a document and a template file, fills the template with data from the
	document and attaches the resulting file to the document.

	:param doctype"     data doctype
	:param name"        data name
	:param template"    name of the template file
	"""
	
	data = frappe.get_doc(doctype, name)
	basic = 0.0
	housing = 0.0
	tranport = 0.0
	vacation_travel = 0.0
	for row in data.salary_detail:
		if row.salary_components == "Basic Salary":
			basic = row.amount
		elif row.salary_components == "Housing Allowance":
			housing = row.amount
		elif row.salary_components == "Transportations Allowance":
			tranport = row.amount
		elif row.salary_components == "Vacation Travel Allowance":
			vacation_travel = row.amount
	
	if data.custom_contract_duration == '1':
		duration = 'one year'
		duration_arabic = 'عام'
	else:
		duration = 'two years'
		duration_arabic = 'عامين'

	data_dict = {
		'custom_posting_date': data.custom_posting_date.strftime("%d-%m-%Y"),
		'custom_date_in_hijri': data.custom_date_in_hijri,
		'custom_name_in_arabic': data.custom_name_in_arabic,
		'custom_c_name': data.custom_c_name,
		'custom_nationality': data.custom_nationality,
		'country_name_in_arabic': frappe.db.get_value("Country",data.custom_nationality,"country_name_in_arabic"),
		'custom_passport_no': data.custom_passport_no,
		'basic': basic,
		'housing': housing,
		'transportation': tranport,
		'vacation_travel': vacation_travel,
		'custom_total_salary': data.custom_total_salary,
		'custom_job_title_on_visa': data.custom_job_title_on_visa,
		'custom_job_title_in_arabic': data.custom_job_title_in_arabic,
		'custom_project_name': data.custom_project_name,
		'project_name_in_arabic': frappe.db.get_value("Project",data.custom_project,"custom_project_name_in_arabic"),
		'custom_leave_days': data.custom_leave_days,
		'contract_duration': duration,
		'contract_duration_in_arabic': duration_arabic,
	}

	template_doc = frappe.get_doc("File", {"attached_to_doctype":"Word Template","attached_to_name":template,"attached_to_field":"word_template_file"})
	template_path = template_doc.get_full_path()

	output_file = _fill_template(template_path, data_dict)
	output_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": "-".join([name, template_doc.file_name]),
		"attached_to_doctype": doctype,
		"attached_to_name": name,
		"content": output_file.getvalue(),
	})
	output_doc.save()

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.personal_email, target.salutation = frappe.db.get_value(
			"Job Offer", source.custom_job_offer, ["applicant_email", "custom_salutation"]
		)
		source_doc = frappe.get_doc("Contract",source_name)
		others = 0
		for sd in source_doc.salary_detail:
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
		"Contract",
		source_name,
		{
			"Contract": {
				"doctype": "Employee",
				"field_map": {"custom_c_name": "first_name",
				  			"custom_name_in_arabic": "name_in_arabic",
							"party_name": "job_applicant",
							"custom_posting_date": "scheduled_confirmation_date",
							"custom_project": "project",
							"custom_passport_no": "passport_number",
							"custom_nationality": "nationality",
							"custom_designation": "designation",
						},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc