# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):

	if not filters:
		filters = {}
	filters = frappe._dict(filters)

	columns = get_columns()

	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Job Requisition"),
			"fieldtype": "Link",
			"fieldname": "job_requisition",
			"options": "Job Requisition",
			"width": 200,
		},
		{
			"label": _("Job Applicant"),
			"fieldtype": "Link",
			"fieldname": "job_applicant",
			"options": "Job Applicant",
			"width": 160,
		},
		{"label": _("Applicant Name"), "fieldtype": "data", "fieldname": "applicant_name", "width": 130},
		{
			"label": _("Applicate Status"),
			"fieldtype": "Data",
			"fieldname": "application_status",
			"width": 130,
		},
		{
			"label": _("Job Offer"),
			"fieldtype": "Link",
			"fieldname": "job_offer",
			"options": "Job Offer",
			"width": 160,
		},
		{
			"label": _("Job Offer Status"),
			"fieldtype": "Data",
			"fieldname": "job_offer_status",
			"width": 140,
		},
		{
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 110,
		},
		{
			"label": _("Project Name"),
			"fieldtype": "Data",
			"fieldname": "project_name",
			"width": 120,
		},
		{
			"label": _("Nationality"),
			"fieldtype": "Data",
			"fieldname": "nationality",
			"width": 100,
		},
		{
			"label": _("Country"),
			"fieldtype": "Link",
			"fieldname": "country",
			"options": "Country",
			"width": 110,
		},
		{
			"label": _("Contract"),
			"fieldtype": "Data",
			"fieldname": "contract",
			"width": 90,
		},	
		{"label": _("Local/Overseas"), "fieldtype": "Data", "fieldname": "local_overseas", "width": 120},
		{"label": _("City"), "fieldtype": "Data", "fieldname": "city", "width": 100},
		{"label": _("Visa Number"), "fieldtype": "Data", "fieldname": "visa_number", "width": 140},
		{"label": _("Visa Title"), "fieldtype": "Data", "fieldname": "visa_title", "width": 150},
		{"label": _("Authorization"), "fieldtype": "Data", "fieldname": "authorization", "width": 130},
		{"label": _("Process Status"), "fieldtype": "date", "fieldname": "process_status", "width": 140},
	]


def get_data(filters):
	data = []
	job_req_list = get_job_requisition(filters)
	jr_list = list(set([details["name"] for details in job_req_list]))
	jo_list = list(set([details["job_opening"] for details in job_req_list]))
	jo_ja_map, ja_list = get_job_applicant(jr_list,jo_list)
	ja_joff_map = get_job_offer(ja_list)
	
	# Sorting the list in descending order
	sorted_jr_list = sorted(jr_list, reverse=True)
	for jr in sorted_jr_list:
		parent_row = get_parent_row(job_req_list, jr, jo_ja_map, ja_joff_map)
		data += parent_row

	return data


def get_parent_row(job_req_list, jr, jo_ja_map, ja_joff_map):
	data = []
	if any(item['name'] == jr for item in job_req_list):
		#get the row
		filtered_data = [row for row in job_req_list if row['name'] == jr]
		row = {
			"job_requisition": filtered_data[0]['name'],
			"job_opening": filtered_data[0]['job_opening'],
			"job_applicant": filtered_data[0]['designation']
		}
		data.append(row)
		child_row = get_child_row(filtered_data[0]['job_opening'] or filtered_data[0]['name'], jo_ja_map, ja_joff_map)
		data += child_row
	return data


def get_child_row(jo, jo_ja_map, ja_joff_map):
	data = []
	if jo in jo_ja_map.keys():
		for ja in jo_ja_map[jo]:
			row = {
				"indent": 1,
				"job_applicant": ja.name,
				"applicant_name": ja.applicant_name,
				"application_status": ja.status,
				"project": ja.project,
				"project_name": ja.project_name
			}
			if ja.name in ja_joff_map.keys():
				jo_detail = ja_joff_map[ja.name][0]
				row["job_offer"] = jo_detail.name
				row["job_offer_status"] = jo_detail.status
				row["offer_date"] = jo_detail.offer_date.strftime("%d-%m-%Y")
				row["designation"] = jo_detail.designation
				row["nationality"] = jo_detail.custom_nationality 
				row["country"] = jo_detail.custom_country
				row["local_overseas"] = jo_detail.custom_applicant_type
				row["contract"] = frappe.db.get_value("Contract",{"custom_job_offer":jo_detail.name},"custom_status")
				row["city"] = jo_detail.custom_current_city
				row["visa_number"] = jo_detail.custom_visa_number
				row["visa_title"] = jo_detail.custom_job_title_on_visa
				row["authorization"] = jo_detail.custom_visa_authorization
				row["process_status"] = jo_detail.custom_current_status
			data.append(row)
	return data

def get_job_requisition(filters):
	if filters.project:
		job_requisition = frappe.get_all(
			"Job Requisition", filters=[["status","=","Open & Approved"],["requested_by","=",filters.project]], fields=["name", "designation"]
		)
	else:
		job_requisition = frappe.get_all(
			"Job Requisition", filters=[["status","=","Open & Approved"]], fields=["name", "designation"]
		)

	for jr in job_requisition:
		if frappe.db.exists("Job Opening", {"status": "Open", "job_requisition": jr.name}):	
			jr["job_opening"] = frappe.get_value("Job Opening",{"status": "Open", "job_requisition": jr.name})
		else:
			jr["job_opening"] = ""

	return job_requisition

def get_job_applicant(jr_list,jo_list):
	jo_ja_map = {}
	ja_list = []

	applicants = frappe.get_all(
		"Job Applicant",
		or_filters=[["job_title", "IN", jo_list],["custom_job_requisition", "IN", jr_list]],
		fields=["name", "job_title","custom_job_requisition", "applicant_name", "status","project","project_name"],
	)

	for applicant in applicants:
		if applicant.job_title not in jo_ja_map.keys():
			jo_ja_map[applicant.job_title] = [applicant]
		else:
			jo_ja_map[applicant.job_title].append(applicant)

		if applicant.custom_job_requisition not in jo_ja_map.keys():
			jo_ja_map[applicant.custom_job_requisition] = [applicant]
		else:
			jo_ja_map[applicant.custom_job_requisition].append(applicant)

		ja_list.append(applicant.name)
	
	return jo_ja_map, ja_list


def get_job_offer(ja_list):
	ja_joff_map = {}

	offers = frappe.get_all(
		"Job Offer",
		filters=[["job_applicant", "IN", ja_list]],
		fields=["name", "job_applicant", "status", "offer_date", "designation","custom_nationality","custom_country","custom_applicant_type",
		  		"custom_current_city","custom_visa_number","custom_job_title_on_visa","custom_visa_authorization","custom_current_status"],
	)

	for offer in offers:
		if offer.job_applicant not in ja_joff_map.keys():
			ja_joff_map[offer.job_applicant] = [offer]
		else:
			ja_joff_map[offer.job_applicant].append(offer)

	return ja_joff_map