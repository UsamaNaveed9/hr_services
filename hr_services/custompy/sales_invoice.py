import frappe
from frappe.utils import get_url_to_form

def new_rec(doc, method):
	if doc.docstatus == 1 and doc.naming_series == 'Draft-.YYYY.-':
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
