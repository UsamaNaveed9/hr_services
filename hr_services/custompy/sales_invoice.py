# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url_to_form
from frappe.utils import flt, get_first_day, get_last_day, nowdate
from frappe import _

def new_rec(doc, method):
	if doc.docstatus == 1 and "Draft" in doc.name:
		# Create a new Sales Invoice with a different naming series
		new_doc = frappe.copy_doc(doc)
		new_doc.naming_series = 'ACC-SINV-.YYYY.-'

		# Save the new document
		new_doc.insert(ignore_permissions=True)
		new_doc.submit()
		
		# Copy attachments from the original draft to the new invoice
		copy_attachments(doc, new_doc)

		# Cancel the existing draft
		frappe.get_doc('Sales Invoice', doc.name).cancel()

		# Delete the existing draft
		frappe.delete_doc('Sales Invoice', doc.name, ignore_permissions=True)

		# Open the new Sales Invoice in the same tab
		url = get_url_to_form("Sales Invoice", new_doc.name)
		# Construct a message with a clickable link
		message = f"Invoice Issued: <a href='{url}'>{new_doc.name}</a>"

		# Display the message with a clickable link
		frappe.msgprint(message, indicator='green')
		
def copy_attachments(source_doc, target_doc):
	# Copy attachments from the source document to the target document
	for attachment in frappe.get_all('File', filters={'attached_to_doctype': source_doc.doctype, 'attached_to_name': source_doc.name}):
		file_doc = frappe.get_doc('File', attachment.name)
		file_copy = frappe.copy_doc(file_doc, ignore_no_copy=False)
		file_copy.attached_to_doctype = target_doc.doctype
		file_copy.attached_to_name = target_doc.name
		file_copy.insert()


#get outstanding total from sales invoice for number card
@frappe.whitelist()
def get_customers_outstanding():
	# Define the date range for the current month
	first_day = get_first_day(nowdate())
	last_day = get_last_day(nowdate())

	# Query to get the outstanding amounts for sales invoices with docstatus = 1
	outstanding_amounts = frappe.db.sql("""
		SELECT SUM(outstanding_amount)
		FROM `tabSales Invoice`
		WHERE docstatus = 1
		AND posting_date BETWEEN %s AND %s
	""", (first_day, last_day))

	# Extract the sum from the query result
	outstanding_sum = flt(outstanding_amounts[0][0]) if outstanding_amounts else 0.0

	# Query to get the grand total amounts for sales invoices with docstatus = 1 and is_return = 1
	return_amounts = frappe.db.sql("""
		SELECT SUM(grand_total)
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_return = 1
		AND posting_date BETWEEN %s AND %s
	""", (first_day, last_day))

	# Extract the sum from the query result
	return_sum = flt(return_amounts[0][0]) if return_amounts else 0.0

	return {
		"value": outstanding_sum + return_sum,
		"fieldtype": "Currency",
		"route_options": {"docstatus": "1","posting_date":["Timespan","this month"],"outstanding_amount":[">",0]},
		"route": ["sales-invoice"]
	}

#function for check the return only invoice amount
def check_outstanding(doc, method):
	if doc.is_return == 1 and doc.return_against:
		sales_inv = frappe.get_doc("Sales Invoice",doc.return_against)
		return_total = -(doc.grand_total)

		if return_total > sales_inv.outstanding_amount:
			frappe.throw(
			_(
				"""The outstanding amount of Sales Invoice <b>{}</b> is <b>{}</b> <br> The return invoice amount is greater than outstanding amount"""
			).format(sales_inv.name, sales_inv.outstanding_amount, return_total),
			title=_("Error")
		)