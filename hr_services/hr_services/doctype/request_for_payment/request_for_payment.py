# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RequestForPayment(Document):
	def on_submit(self):
		#creating journal entry on the approval of request of payment
		new_doc = frappe.new_doc("Journal Entry")
		new_doc.voucher_type = "Journal Entry"
		new_doc.posting_date = self.date
		new_doc.company = self.company
		for it in self.items:
			row = new_doc.append("accounts",{})
			row.account = frappe.db.get_value("Item",{"name":it.item},"account_for_jv")
			row.debit_in_account_currency = it.amount

		row = new_doc.append("accounts",{})
		row.account = frappe.db.get_value("Company",{"name":self.company},"default_bank_account")
		row.credit_in_account_currency = self.total_amount
				
		new_doc.save()
		new_doc.submit()

		#creating sales invoice on the approval of request of payment
		si = frappe.new_doc("Sales Invoice")
		si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
		si.set_posting_time = 1
		si.posting_date = self.date
		si.due_date = self.date
		si.issue_date = self.date
		si.project = self.project
			
		for it in self.items:
			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = it.item
			si_item.employee_id = it.employee_no
			si_item.employee_name = it.employee_name
			si_item.qty = it.qty
			si_item.rate = it.rate	
			si.append("items", si_item)

		si_tax = frappe.new_doc("Sales Taxes and Charges")
		si_tax.charge_type = "On Net Total"
		si_tax.account_head = "VAT 15% - ERC"
		si_tax.description = "VAT 15%"
		si_tax.rate = 15
		si.append("taxes", si_tax)

		si.save(ignore_permissions=True)
