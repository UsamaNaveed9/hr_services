// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Costing Sheet ERC"] = {
	"filters": [
		{
			"fieldname":"sheet_type",
			"label": __("Sheet Type"),
			"fieldtype": "Select",
			"options": "Cenomi\nACWA\nMisk",
			"reqd": 1,
			"default": "Cenomi",
		},
		{
			"fieldname": "emp_type",
			"label": __("Employment Type"),
			"fieldtype": "Select",
			"options": "Full Time\nPart Time",
			"hidden": true,  // Initially hidden
			"depends_on": "eval:doc.sheet_type=='Misk'",
			"default": "Full Time"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
	]
};