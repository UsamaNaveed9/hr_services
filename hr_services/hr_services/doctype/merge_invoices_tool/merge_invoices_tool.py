# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _
from frappe.utils import get_url_to_form

class MergeInvoicesTool(Document):
	pass

@frappe.whitelist()
def merge_invoices(due_date,customer,sales_invoices):
	invs = json.loads(sales_invoices)
	#frappe.errprint(invs)
	# Get the set of unique 'po_no' values
	unique_po_nos = set(rec['po_no'] for rec in invs)
	msg = ""
	# Check if there is only one unique 'po_no'
	if len(unique_po_nos) == 1:
		po_no = list(unique_po_nos)

		si = frappe.new_doc("Sales Invoice")
		si.naming_series = "ACC-SINV-.YYYY.-"
		si.customer = customer
		si.set_posting_time = 1
		si.posting_date = due_date
		si.due_date = due_date
		si.issue_date = due_date
		si.is_pos = 0
		si.po_no = po_no[0]

		for sal_inv in invs:
			sales_doc = frappe.get_doc("Sales Invoice",sal_inv["sales_invoice"])
			si.project = sales_doc.project
			si.print_customer = sales_doc.print_customer
			items = sales_doc.items
			for inv_it in items:
				si_item = frappe.new_doc("Sales Invoice Item")
				si_item.item_code = inv_it.item_code
				si_item.description = inv_it.description
				si_item.qty = inv_it.qty
				si_item.rate = inv_it.rate
				si_item.employee_id = inv_it.employee_id
				si_item.employee_name = inv_it.employee_name
				si_item.custom_rfp = inv_it.custom_rfp
				si.append("items", si_item)

		si_tax = frappe.new_doc("Sales Taxes and Charges")
		si_tax.charge_type = "On Net Total"
		si_tax.account_head = "VAT 15% - ERC"
		si_tax.description = "VAT 15%"
		si_tax.rate = 15
		si.append("taxes", si_tax)

		si.save(ignore_permissions=True)

		remarks = "This invoice created with the merge of these invoices: "
		if si.name:
			for sal_inv in invs:
				remarks = remarks + " " + sal_inv["sales_invoice"]
				copy_attachments(sal_inv["sales_invoice"], si)
				# Delete the merged draft invoice
				frappe.delete_doc('Sales Invoice', sal_inv["sales_invoice"], ignore_permissions=True)
			si.remarks = remarks
			si.save(ignore_permissions=True)
			si.submit()
			# Open the new Sales Invoice in the same tab
			url = get_url_to_form("Sales Invoice", si.name)
			# Construct a message with a clickable link
			msg = f"Merge Invoice Created Successfully: <a href='{url}'>{si.name}</a>"
	else:
		frappe.throw(_("PO Nos must be same"))

	return msg

def copy_attachments(source_doc, target_doc):
	# Copy attachments from the source document to the target document
	for attachment in frappe.get_all('File', filters={'attached_to_doctype': "Sales Invoice", 'attached_to_name': source_doc}):
		file_doc = frappe.get_doc('File', attachment.name)
		file_copy = frappe.copy_doc(file_doc, ignore_no_copy=False)
		file_copy.attached_to_doctype = target_doc.doctype
		file_copy.attached_to_name = target_doc.name
		file_copy.insert()


