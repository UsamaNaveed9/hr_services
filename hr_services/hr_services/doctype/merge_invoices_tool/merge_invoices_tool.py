# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _

class MergeInvoicesTool(Document):
	pass

@frappe.whitelist()
def merge_invoices(due_date,customer,sales_invoices):
	invs = json.loads(sales_invoices)
	frappe.errprint(invs)

	# Get the set of unique 'po_no' values
	unique_po_nos = set(rec['po_no'] for rec in invs)

	# Check if there is only one unique 'po_no'
	if len(unique_po_nos) == 1:
		frappe.errprint(unique_po_nos)
	else:
		frappe.throw(_("PO Nos must be same"))


