# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import getdate, nowdate

def execute(filters=None):
	return _execute(filters)

def _execute(filters):
	if not filters:
		filters = frappe._dict({})

	invoice_list = get_invoices(filters)
	columns = get_columns(invoice_list)
	
	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	company_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")
	
	data = []
	for inv in invoice_list:
		row = {
			"invoice": inv.name,
			"posting_date": inv.posting_date,
			"customer": inv.customer,
			"status": inv.status,
			"remarks": inv.remarks,
			"currency": company_currency,
			"net_total": inv.total,
			"tax_total": inv.total_taxes_and_charges,
			"grand_total": inv.grand_total,
			"outstanding_amount": inv.outstanding_amount,
			"date_of_com": inv.date_of_communication,
			"uploaded_date": inv.uploaded_date
		}
		#communicated is done or not
		if inv.is_shared_with_client == 1:
			row.update({"communicated": "Yes"})
		else:
			row.update({"communicated": "No"})

		#Include in tracker or not
		if inv.custom_not_for_tracker == 0:
			row.update({"tracker_status": "Yes"})
		else:
			row.update({"tracker_status": "No"})

		#calculate the paid amount
		paid = 0
		paid = inv.grand_total - inv.outstanding_amount

		#calculate the ageing from communicaton date
		days_difference = 0
		if inv.date_of_communication:
			# Convert the date string to a Frappe date object
			given_date = getdate(inv.date_of_communication)

			# Get today's date using Frappe
			today_date = getdate(nowdate())

			# Calculate the difference in days
			days_difference = (today_date - given_date).days

		row.update({
			"total_paid": paid,
			"ageing": days_difference
		})

		#get all payment entries of sales invoice
		py_entries = get_payment_entries(inv.name)
		if py_entries:
			row.update({
				"date_of_payment": py_entries[0]['posting_date']
			})
		elif inv.outstanding_amount < inv.grand_total:
			row.update({
				"date_of_payment": inv.posting_date
			})

		data.append(row)

	return columns, data


def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Invoice No"),
			"fieldname": "invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 170,
		},
		{"label": _("Tracker Status"), "fieldname": "tracker_status", "fieldtype": "Data", "width": 100},
		{"label": _("Invoice Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"label": _("Payment Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Total"),
			"fieldname": "net_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("VAT Amount"),
			"fieldname": "tax_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Total with VAT"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Total Paid"),
			"fieldname": "total_paid",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Balance Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Date of Payment"),
			"fieldname": "date_of_payment",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Communicated"),
			"fieldname": "communicated",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Date of Communication"),
			"fieldname": "date_of_com",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Ageing"),
			"fieldname": "ageing",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("Uploaded Date"),
			"fieldname": "uploaded_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
	]

	return columns


def get_conditions(filters):
	conditions = ""

	if filters.get("company"):
		conditions += " company=%(company)s"

	if filters.get("customer"):
		conditions += " and customer = %(customer)s"

	if filters.get("status"):
		if filters.get("status") == "Paid":	
			conditions += " and docstatus = 1 and outstanding_amount = 0"
		elif filters.get("status") == "Unpaid":
			conditions += " and ((docstatus = 1 and outstanding_amount > 0) or (docstatus = 0 and show_in_report = 1))"	

	#frappe.errprint(conditions)
	return conditions


def get_invoices(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql(
		"""
		select name, posting_date, customer, status, remarks, total, is_pos,
		total_taxes_and_charges, grand_total, outstanding_amount, paid_amount, custom_not_for_tracker,
		is_shared_with_client, date_of_communication, uploaded_date, company
		from `tabSales Invoice`
		where {0}
		order by posting_date desc, name desc""".format(
			conditions
		),
		filters,
		as_dict=1,
	)

def get_payment_entries(inv):
	return frappe.db.sql(
		"""
		select pe.name, pe.posting_date, pe.paid_amount
		from `tabPayment Entry` as pe
		join `tabPayment Entry Reference` as per
		on pe.name = per.parent
		where per.reference_name = '{0}'
		order by posting_date desc""".format(inv),
		as_dict=1,
	)	