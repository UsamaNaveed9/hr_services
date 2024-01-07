// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Invoices Detail"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nPaid\nUnpaid"
		},
	]
};
