# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, msgprint, qb
import json

class RequestForPayment(Document):
	def on_submit(self):
		if self.expense_type == "Operational Expense" or self.expense_type == "Recruitment Expense" or self.expense_type == "Reimbursement Expense":
			#creating journal entry on the approval of request of payment
			if self.coa_for_jv:
				new_doc = frappe.new_doc("Journal Entry")
				new_doc.voucher_type = "Journal Entry"
				new_doc.posting_date = self.date
				new_doc.company = self.company
				for it in self.items:
					row = new_doc.append("accounts",{})
					row.account = frappe.db.get_value("Item",{"name":it.item},"account_for_jv")
					row.debit_in_account_currency = it.amount
					row.reference_type = "Request For Payment"
					row.reference_name = self.name

					row = new_doc.append("accounts",{})
					row.account = self.coa_for_jv
					row.credit_in_account_currency = it.amount

				#new_doc.custom_request_for_payment = self.name
				new_doc.user_remark = f"{self.expense_type} of Client {self.project_name} from Request for Payment "		
				new_doc.save(ignore_permissions=True)
				copy_attachments(self, new_doc)
				#new_doc.submit()
			else:
				frappe.throw(_("Bank is Manadatory"))

			#creating sales invoice on the approval of request of payment and skip for project PROJ-0018 (Elite HQ)
			if self.project != "PROJ-0018" and self.invoice_to_client == "Yes":
				si = frappe.new_doc("Sales Invoice")
				si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
				si.set_posting_time = 1
				si.posting_date = self.date
				si.due_date = self.date
				si.issue_date = self.date
				si.project = self.project
				si.is_pos = 0
					
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

				si.custom_request_for_payment = self.name
				si.remarks = f"{self.expense_type} from Request for Payment"
				si.save(ignore_permissions=True)
				copy_attachments(self, si)
		elif self.expense_type == "Supplier Payment":
			#creating Payment entry on the approval of request of payment
			new_doc = frappe.new_doc("Payment Entry")
			new_doc.payment_type = "Pay"
			new_doc.posting_date = self.date
			new_doc.company = self.company
			new_doc.mode_of_payment = "Bank"
			new_doc.party_type = "Supplier"
			new_doc.party = self.supplier
			new_doc.paid_from = self.coa_for_jv
			new_doc.paid_from_account_currency = "SAR"
			new_doc.paid_to = "2220102 - Local Suppliers - ERC"
			new_doc.paid_to_account_currency = "SAR"
			new_doc.paid_amount = self.total_amount
			new_doc.source_exchange_rate = 1
			new_doc.received_amount = self.total_amount
			for inv in self.invoices:
				row = new_doc.append("references",{})
				row.reference_doctype = "Purchase Invoice"
				row.reference_name = inv.purchase_invoice
				row.allocated_amount = inv.paid_amount

			new_doc.reference_no = self.name
			new_doc.reference_date = self.date
			new_doc.custom_request_for_payment = self.name
			new_doc.remarks = f"{self.expense_type} approved by Request For Payment"
			new_doc.save(ignore_permissions=True)
			new_doc.submit()
			copy_attachments(self, new_doc)

			#creating sales invoices on the list of invoices after the approval of request of payment
			if self.project != "PROJ-0018" and self.invoice_to_client == "Yes":
				for inv in self.invoices:
					si = frappe.new_doc("Sales Invoice")
					si.customer = frappe.db.get_value("Project",{"name":inv.project},"customer")
					si.set_posting_time = 1
					si.posting_date = self.date
					si.due_date = self.date
					si.issue_date = self.date
					si.project = inv.project
					si.is_pos = 0

					pur_doc = frappe.get_doc("Purchase Invoice",inv.purchase_invoice)
					#getting the tax rate if tax applied on invoice
					tax_rate = 0
					if pur_doc.taxes:
						tax_rate = pur_doc.taxes[0].rate

					items = pur_doc.items
					for inv_it in items:
						si_item = frappe.new_doc("Sales Invoice Item")
						si_item.item_code = inv_it.item_code
						si_item.qty = inv_it.qty
						if tax_rate > 0:
							si_item.rate = inv_it.rate + (inv_it.rate * (tax_rate / 100))
						else:	
							si_item.rate = inv_it.rate
						si_item.employee_id = inv_it.employee_no
						si_item.employee_name = inv_it.employee_name
						si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.custom_request_for_payment = self.name
					si.remarks = f"{self.expense_type} from Request for Payment"
					si.save(ignore_permissions=True)
					#copy_attachments(self, si)
		elif self.expense_type == "Payment For Part Timer":
			#creating journal entry on the approval of request of payment
			if self.coa_for_jv:
				new_doc = frappe.new_doc("Journal Entry")
				new_doc.voucher_type = "Journal Entry"
				new_doc.posting_date = self.date
				new_doc.company = self.company
				for it in self.employees:
					row = new_doc.append("accounts",{})
					row.account = "51-0101 - OPE-ME- Basic Salary - ERC"
					row.debit_in_account_currency = it.amount
					row.reference_type = "Request For Payment"
					row.reference_name = self.name

					row = new_doc.append("accounts",{})
					row.account = self.coa_for_jv
					row.credit_in_account_currency = it.amount

				#new_doc.custom_request_for_payment = self.name
				new_doc.user_remark = f"{self.expense_type} of Client {self.project_name} from Request for Payment"
				new_doc.save(ignore_permissions=True)
				copy_attachments(self, new_doc)
				#new_doc.submit()
			else:
				frappe.throw(_("Bank is Manadatory"))	

			#creating sales invoices on the approval of request of payment and skip for project PROJ-0018 (Elite HQ)
			#one sales invoice for one employee record.
			if self.project != "PROJ-0018" and self.invoice_to_client == "Yes":
				for emp in self.employees:
					si = frappe.new_doc("Sales Invoice")
					si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
					si.set_posting_time = 1
					si.posting_date = self.date
					si.due_date = self.date
					si.issue_date = self.date
					si.project = self.project
					si.is_pos = 0
					si.po_no = emp.po_no

					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 34
					si_item.qty = emp.working_days
					si_item.rate = frappe.db.get_value("PO Management",{"name": emp.po_mgt},"invoicing_rate")
					si_item.employee_id = emp.employee_no
					si_item.employee_name = emp.employee_name
					si.append("items", si_item)

					si_tax = frappe.new_doc("Sales Taxes and Charges")
					si_tax.charge_type = "On Net Total"
					si_tax.account_head = "VAT 15% - ERC"
					si_tax.description = "VAT 15%"
					si_tax.rate = 15
					si.append("taxes", si_tax)

					si.custom_request_for_payment = self.name
					si.remarks = f"{self.expense_type} from Request for Payment"
					si.save(ignore_permissions=True)
					copy_attachments(self, si)
					if si.name:
						po_mdoc = frappe.get_doc("PO Management", emp.po_mgt)
						po_mdoc.used_units = po_mdoc.used_units + emp.working_days
						po_mdoc.remaining_units = po_mdoc.remaining_units - emp.working_days
						po_mdoc.save(ignore_permissions=True)
						if po_mdoc.remaining_units == 0:
							po_mdoc.status = "Completed"
							po_mdoc.save(ignore_permissions=True)
		elif self.expense_type == "Employee Advance":
			#creating loan on each employee
			#Sales Invoice agains employees that have advance type == "Housing Advance"
			si = frappe.new_doc("Sales Invoice")
			si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
			si.set_posting_time = 1
			si.posting_date = self.date
			si.due_date = self.date
			si.issue_date = self.date
			si.project = self.project
			si.is_pos = 0

			for adv in self.advances:
				#creating loan on each employee 
				ln = frappe.new_doc("Loan")
				ln.applicant_type = "Employee"
				ln.applicant = adv.employee_no
				ln.applicant_name = adv.employee_name
				ln.posting_date = self.date
				ln.repay_from_salary = 1
				ln.loan_type = adv.advance_type
				ln.loan_amount = adv.advance_amount
				ln.repayment_method = "Repay Fixed Amount per Period"
				ln.monthly_repayment_amount = adv.monthly_repay_amount
				ln.repayment_start_date = adv.repayment_start_date
				ln.custom_request_for_payment = self.name
				ln.save(ignore_permissions=True)
				ln.submit()

				if ln.name:
					#creating Loan Disbursement after creating loan
					ln_d = frappe.new_doc("Loan Disbursement")
					ln_d.against_loan = ln.name
					ln_d.disbursement_date = self.date
					ln_d.disbursed_amount = adv.advance_amount
					ln_d.save(ignore_permissions=True)
					ln_d.submit()

				#adding items in sales invoice if advance type == "Housing Advance"
				if adv.advance_type == "Housing Advance":
					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 891
					si_item.qty = 1
					si_item.rate = adv.advance_amount
					si_item.employee_id = adv.employee_no
					si_item.employee_name = adv.employee_name
					si.append("items", si_item)
			#adding 15% tax on the sales invoice
			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.custom_request_for_payment = self.name
			si.remarks = f"{self.expense_type} from Request for Payment"
			#if items exist then invoice save in the system otherwise skip it.
			if len(si.items) > 0 and self.project != "PROJ-0018" and self.invoice_to_client == "Yes":
				si.save(ignore_permissions=True)
				copy_attachments(self, si)
		elif self.expense_type == "Split Amount b/w Client and Employee":
			#creating journal entry on the approval of request of payment for items that invoice to client
			if self.coa_for_jv:
				new_doc = frappe.new_doc("Journal Entry")
				new_doc.voucher_type = "Journal Entry"
				new_doc.posting_date = self.date
				new_doc.company = self.company
				for it in self.items:
					row = new_doc.append("accounts",{})
					row.account = frappe.db.get_value("Item",{"name":it.item},"account_for_jv")
					row.debit_in_account_currency = it.amount
					row.reference_type = "Request For Payment"
					row.reference_name = self.name

					row = new_doc.append("accounts",{})
					row.account = self.coa_for_jv
					row.credit_in_account_currency = it.amount

				new_doc.user_remark = f"{self.expense_type} of Client {self.project_name} from Request for Payment "		
				new_doc.save(ignore_permissions=True)
				copy_attachments(self, new_doc)
				#new_doc.submit()
			else:
				frappe.throw(_("Bank is Manadatory"))

			#creating sales invoice on the approval of request of payment and skip for project PROJ-0018 (Elite HQ)	for items
			#creating loan on each employee
			#Also adding loan amount in sales invoice if advance type == "Housing Advance"
			si = frappe.new_doc("Sales Invoice")
			si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
			si.set_posting_time = 1
			si.posting_date = self.date
			si.due_date = self.date
			si.issue_date = self.date
			si.project = self.project
			si.is_pos = 0

			for it in self.items:
				si_item = frappe.new_doc("Sales Invoice Item")
				si_item.item_code = it.item
				si_item.employee_id = it.employee_no
				si_item.employee_name = it.employee_name
				si_item.qty = it.qty
				si_item.rate = it.rate	
				si.append("items", si_item)

			for adv in self.advances:
				#creating loan on each employee 
				ln = frappe.new_doc("Loan")
				ln.applicant_type = "Employee"
				ln.applicant = adv.employee_no
				ln.applicant_name = adv.employee_name
				ln.posting_date = self.date
				ln.repay_from_salary = 1
				ln.loan_type = adv.advance_type
				ln.loan_amount = adv.advance_amount
				ln.repayment_method = "Repay Fixed Amount per Period"
				ln.monthly_repayment_amount = adv.monthly_repay_amount
				ln.repayment_start_date = adv.repayment_start_date
				ln.custom_request_for_payment = self.name
				ln.save(ignore_permissions=True)
				ln.submit()

				if ln.name:
					#creating Loan Disbursement after creating loan
					ln_d = frappe.new_doc("Loan Disbursement")
					ln_d.against_loan = ln.name
					ln_d.disbursement_date = self.date
					ln_d.disbursed_amount = adv.advance_amount
					ln_d.save(ignore_permissions=True)
					ln_d.submit()

				#adding items in sales invoice if advance type == "Housing Advance"
				if adv.advance_type == "Housing Advance":
					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = 891
					si_item.qty = 1
					si_item.rate = adv.advance_amount
					si_item.employee_id = adv.employee_no
					si_item.employee_name = adv.employee_name
					si.append("items", si_item)
			#adding 15% tax on the sales invoice
			si_tax = frappe.new_doc("Sales Taxes and Charges")
			si_tax.charge_type = "On Net Total"
			si_tax.account_head = "VAT 15% - ERC"
			si_tax.description = "VAT 15%"
			si_tax.rate = 15
			si.append("taxes", si_tax)

			si.custom_request_for_payment = self.name
			si.remarks = f"{self.expense_type} from Request for Payment"
			#if items exist then invoice save in the system otherwise skip it.
			if len(si.items) > 0 and self.project != "PROJ-0018" and self.invoice_to_client == "Yes":
				si.save(ignore_permissions=True)
				copy_attachments(self, si)


	def submit(self):
		if (self.expense_type == "Operational Expense" or self.expense_type == "Recruitment Expense" or self.expense_type == "Reimbursement Expense") and len(self.items) > 10:
			msgprint(_("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Request For Payment Record and revert to the Previous stage"))
			self.queue_action('submit', timeout=20000)
		elif self.expense_type == "Supplier Payment" and len(self.invoices) > 5:
			msgprint(_("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Request For Payment Record and revert to the Previous stage"))
			self.queue_action('submit', timeout=20000)
		elif self.expense_type == "Payment For Part Timer" and len(self.employees) > 5:
			msgprint(_("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Request For Payment Record and revert to the Previous stage"))
			self.queue_action('submit', timeout=20000)
		elif self.expense_type == "Employee Advance" and len(self.advances) > 5:
			msgprint(_("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Request For Payment Record and revert to the Previous stage"))
			self.queue_action('submit', timeout=20000)
		else:
			self._submit()
				

def copy_attachments(source_doc, target_doc):
	# Copy attachments from the source document to the target document
	for attachment in frappe.get_all('File', filters={'attached_to_doctype': source_doc.doctype, 'attached_to_name': source_doc.name}):
		file_doc = frappe.get_doc('File', attachment.name)
		file_copy = frappe.copy_doc(file_doc, ignore_no_copy=False)
		file_copy.attached_to_doctype = target_doc.doctype
		file_copy.attached_to_name = target_doc.name
		file_copy.insert()

@frappe.whitelist()
def update_linked_records(self):
	self = json.loads(self)
	if frappe.db.exists("Sales Invoice", {"custom_request_for_payment": self["name"]}):
		#get sales invoices
		si_doc = frappe.get_doc("Sales Invoice", {"custom_request_for_payment": self["name"]})
		# Remove existing child table items
		si_doc.items = []
		
		# Append new items
		for it in self["items"]:
			si_item = frappe.new_doc("Sales Invoice Item")
			si_item.item_code = it["item"]
			si_item.qty = it["qty"]
			si_item.rate = it["rate"]
			if "employee_no" in it:
				si_item.employee_id = it["employee_no"]
			if "employee_name" in it:	
				si_item.employee_name = it["employee_name"]
			si_doc.append("items", si_item)

		si_doc.save(ignore_permissions=True)
	
	# Get journal entries
	journals = frappe.get_all("Journal Entry Account",
							   filters={"reference_type": "Request For Payment",
										"reference_name": self["name"],
										"docstatus": 0},
							   distinct=True,
							   pluck="parent")
	
	for journal_name in journals:
		# Get journal entry
		je_doc = frappe.get_doc("Journal Entry", journal_name)
		
		# Remove existing child table items
		je_doc.accounts = []
		
		# Append new items
		for it in self["items"]:
			row = je_doc.append("accounts",{})
			row.account = frappe.db.get_value("Item",{"name":it["item"]},"account_for_jv")
			row.debit_in_account_currency = it["amount"]
			row.reference_type = "Request For Payment"
			row.reference_name = self["name"]

			row = je_doc.append("accounts",{})
			row.account = self["coa_for_jv"]
			row.credit_in_account_currency = it["amount"]
		
		# Save journal entry
		je_doc.save(ignore_permissions=True)
	frappe.db.set_value("Request For Payment", self["name"], "resubmitted_and_updated", 1, update_modified=False)
	status = "Done"
	return 	status