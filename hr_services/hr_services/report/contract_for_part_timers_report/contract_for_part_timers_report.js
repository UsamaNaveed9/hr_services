// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Contract For Part Timers Report"] = {
	"filters": [
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nUnsigned\nActive\nInactive",
		}

	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status" && data && data.status == "Unsigned") {
			value = "<span style='color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Active") {
			value = "<span style='color:green'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Inactive") {
			value = "<span style='color:orange'>" + value + "</span>";
		}

		return value;
	},
};
