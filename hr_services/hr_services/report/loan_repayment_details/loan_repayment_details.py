# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Posting Date"), "fieldtype": "Date", "fieldname": "posting_date", "width": 120},
		{
			"label": _("Loan Repayment"),
			"fieldtype": "Link",
			"fieldname": "loan_repayment",
			"options": "Loan Repayment",
			"width": 130,
		},
		{
			"label": _("Against Loan"),
			"fieldtype": "Link",
			"fieldname": "against_loan",
			"options": "Loan",
			"width": 180,
		},
		{"label": _("Applicant"), "fieldtype": "Data", "fieldname": "applicant", "width": 150},
		{"label": _("Applicant Name"), "fieldtype": "Data", "fieldname": "applicant_name", "width": 150},
		{
			"label": _("Principal Amount"),
			"fieldtype": "Currency",
			"fieldname": "principal_amount",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"fieldname": "paid_amount",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Remaining Amount"),
			"fieldtype": "Currency",
			"fieldname": "remaining_amount",
			"options": "currency",
			"width": 140,
		},
	]


def get_data(filters):
	data = []

	query_filters = {
		"docstatus": 1,
		"company": filters.get("company"),
	}

	if filters.get("applicant"):
		query_filters.update({"applicant": filters.get("applicant")})

	loan_repayments = frappe.get_all(
		"Loan Repayment",
		filters=query_filters,
		fields=[
			"posting_date",
			"applicant",
			"name",
			"against_loan",
			"pending_principal_amount",
			"amount_paid",
		],
		order_by='posting_date asc'
	)

	for repayment in loan_repayments:
		row = {
			"posting_date": repayment.posting_date,
			"loan_repayment": repayment.name,
			"applicant": repayment.applicant,
			"applicant_name": frappe.db.get_value("Loan",repayment.against_loan,"applicant_name"),
			"against_loan": repayment.against_loan,
			"principal_amount": repayment.pending_principal_amount,
			"paid_amount": repayment.amount_paid,
			"remaining_amount": repayment.pending_principal_amount - repayment.amount_paid,
		}

		data.append(row)

	return data