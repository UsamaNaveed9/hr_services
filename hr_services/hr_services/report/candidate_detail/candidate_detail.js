// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Candidate Detail"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"on_date",
			"label": __("On Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
			"reqd": 1,
			"hidden": 1,
		},
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
		}
	]
};
