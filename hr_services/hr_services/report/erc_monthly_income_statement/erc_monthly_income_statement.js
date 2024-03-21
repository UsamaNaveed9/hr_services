// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["ERC Monthly Income Statement"] = {
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
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			"reqd": 1
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options": [
				{ "value": "One Month", "label": __("One Month") },
				{ "value": "Multi Months", "label": __("Multi Months") }
			],
			"default": "One Month",
			"reqd": 1
		},
		{
			"fieldname":"from_month",
			"label": __("Start Month"),
			"fieldtype": "Select",
			"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": "January",
			"reqd": 1
		},
		{
			"fieldname":"to_month",
			"label": __("End Month"),
			"fieldtype": "Select",
			"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": "January",
			"reqd": 1,
			"depends_on": "eval:doc.periodicity == 'Multi Months'"
		}
	]
};
