// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["WL Iqama Costs and Durations"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_default('company')
		},
	]
};
