# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RequestForPayment(Document):
	def on_submit(self):
		if self.expense_type == "Operational Expense" or self.expense_type == "Recruitment Expense" or self.expense_type == "Reimbursement Expense":
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
				row.credit_in_account_currency = it.amount

			new_doc.custom_request_for_payment = self.name
			new_doc.user_remark = f"{self.expense_type} of Client {self.project_name} from Request for Payment "		
			new_doc.save(ignore_permissions=True)
			#new_doc.submit()

			#creating sales invoice on the approval of request of payment and skip for project PROJ-0018 (Elite HQ)
			if self.project != "PROJ-0018":
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

				si.custom_request_for_payment = self.name
				si.remarks = f"{self.expense_type} from Request for Payment"
				si.save(ignore_permissions=True)
		elif self.expense_type == "Supplier Payment":
			#creating Payment entry on the approval of request of payment
			new_doc = frappe.new_doc("Payment Entry")
			new_doc.payment_type = "Pay"
			new_doc.posting_date = self.date
			new_doc.company = self.company
			new_doc.mode_of_payment = "Bank"
			new_doc.party_type = "Supplier"
			new_doc.party = self.supplier
			new_doc.paid_from = "11010201 - ALINMA - ERC"
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
				row.allocated_amount = inv.outstanding_amount

			new_doc.reference_no = self.name
			new_doc.reference_date = self.date
			new_doc.custom_request_for_payment = self.name
			new_doc.remarks = f"{self.expense_type} approved by Request For Payment"
			new_doc.save(ignore_permissions=True)
			new_doc.submit()

			#creating sales invoices on the list of invoices after the approval of request of payment
			for inv in self.invoices:
				si = frappe.new_doc("Sales Invoice")
				si.customer = frappe.db.get_value("Project",{"name":inv.project},"customer")
				si.set_posting_time = 1
				si.posting_date = self.date
				si.due_date = self.date
				si.issue_date = self.date
				si.project = inv.project

				pur_doc = frappe.get_doc("Purchase Invoice",inv.purchase_invoice)
				items = pur_doc.items
				for inv_it in items:
					si_item = frappe.new_doc("Sales Invoice Item")
					si_item.item_code = inv_it.item_code
					si_item.qty = inv_it.qty
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
		elif self.expense_type == "Payment For Part Timer":
			#creating journal entry on the approval of request of payment
			new_doc = frappe.new_doc("Journal Entry")
			new_doc.voucher_type = "Journal Entry"
			new_doc.posting_date = self.date
			new_doc.company = self.company
			for it in self.employees:
				row = new_doc.append("accounts",{})
				row.account = "51-0101 - OPE-ME- Basic Salary - ERC"
				row.debit_in_account_currency = it.amount

				row = new_doc.append("accounts",{})
				row.account = frappe.db.get_value("Company",{"name":self.company},"default_bank_account")
				row.credit_in_account_currency = it.amount

			new_doc.custom_request_for_payment = self.name
			new_doc.user_remark = f"{self.expense_type} of Client {self.project_name} from Request for Payment "		
			new_doc.save(ignore_permissions=True)
			#new_doc.submit()

			#creating sales invoices on the approval of request of payment and skip for project PROJ-0018 (Elite HQ)
			#one sales invoice for one employee record.
			if self.project != "PROJ-0018":
				for emp in self.employees:
					si = frappe.new_doc("Sales Invoice")
					si.customer = frappe.db.get_value("Project",{"name":self.project},"customer")
					si.set_posting_time = 1
					si.posting_date = self.date
					si.due_date = self.date
					si.issue_date = self.date
					si.project = self.project

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

			for adv in self.advances:
				#creating loan on each employee 
				ln = frappe.new_doc("Loan")
				ln.applicant_type = "Employee"
				ln.applicant = adv.employee_no
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
			if len(si.items) > 0 and self.project != "PROJ-0018":
				si.save(ignore_permissions=True)
				
