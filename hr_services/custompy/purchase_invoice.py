# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, nowdate

def check_inv(doc, method):
	if doc.bill_no and frappe.db.exists("Purchase Invoice",{"supplier": doc.supplier, "bill_no": doc.bill_no}):
		frappe.throw(_("{0} Supplier Invoice No {1} already exist").format(doc.supplier, doc.bill_no))


#get outstanding total from purchase invoice for number card
@frappe.whitelist()
def get_suppliers_outstanding():
	# Define the date range for the current month
	first_day = get_first_day(nowdate())
	last_day = get_last_day(nowdate())

	# Query to get the outstanding amounts for purchase invoices with docstatus = 1
	outstanding_amounts = frappe.db.sql("""
		SELECT SUM(outstanding_amount)
		FROM `tabPurchase Invoice`
		WHERE docstatus = 1
		AND posting_date BETWEEN %s AND %s
	""", (first_day, last_day))

	# Extract the sum from the query result
	outstanding_sum = flt(outstanding_amounts[0][0]) if outstanding_amounts else 0.0

	# Query to get the grand total amounts for purchase invoices with docstatus = 1 and is_return = 1
	return_amounts = frappe.db.sql("""
		SELECT SUM(grand_total)
		FROM `tabPurchase Invoice`
		WHERE docstatus = 1 AND is_return = 1
		AND posting_date BETWEEN %s AND %s
	""", (first_day, last_day))

	# Extract the sum from the query result
	return_sum = flt(return_amounts[0][0]) if return_amounts else 0.0


	return {
		"value": outstanding_sum + return_sum,
		"fieldtype": "Currency",
		"route_options": {"docstatus": "1","posting_date":["Timespan","this month"],"outstanding_amount":[">",0]},
		"route": ["purchase-invoice"]
	}