# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint

def execute(filters=None):
	columns = get_columns()
	data = []

	customers = get_customers()
	invoice_amt_list = get_invoices_amt(customers)
	#frappe.errprint(invoice_amt_list)
	for inv_amt in invoice_amt_list:
		row = {
			"client_name": inv_amt.project_name,
			"shared_with_client": inv_amt.shared_with_client,
			"without_po": inv_amt.without_po,
			"not_shared_yet": inv_amt.not_yet_shared,
			"total": inv_amt.shared_with_client + inv_amt.without_po + inv_amt.not_yet_shared,
			"uploaded_on_client": inv_amt.uploaded_on_client
		}
		data.append(row)

	return columns, data

def get_columns():
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Client Name"),
			"fieldname": "client_name",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 220,
		},
		{
			"label": _("Shared with Client"),
			"fieldname": "shared_with_client",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"label": _("Without PO"),
			"fieldname": "without_po",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 160,
		},
		{
			"label": _("New Invoices Not Yet Shared"),
			"fieldname": "not_shared_yet",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 220,
		},
		{
			"label": _("Total as in Tracker"),
			"fieldname": "total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 160,
		},
		{
			"label": _("Uploaded on Client Portal"),
			"fieldname": "uploaded_on_client",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200,
		},
	]

	return columns

def get_customers():
	customers = frappe.get_all('Customer', 
							filters={'disabled': 0, 'is_standard_invoice_customer':1}, 
							fields=['name', 'customer_name','project_name','project_id'],
							order_by='project_id')
	return customers

def get_invoices_amt(customers):
	po_projects_ids = {'PROJ-0001', 'PROJ-0002', 'PROJ-0012', 'PROJ-0013'}

	po_customers = []
	customers_to_remove = []

	for customer in customers:
		if customer['project_id'] in po_projects_ids:
			po_customers.append(customer)
			customers_to_remove.append(customer)

	for customer in customers_to_remove:
		customers.remove(customer)

	# Fetch submitted outstanding amounts of shared with client for non po customers
	shared_with_clients = frappe.get_all('Sales Invoice',
										 filters={'customer': ('in', [customer['name'] for customer in customers]),
												  'docstatus': 1, 'is_shared_with_client': 1, 'custom_not_for_tracker': 0},
										 fields=['customer', 'sum(outstanding_amount) as outstanding_amount'],
										 group_by='customer')

	# Fetch outstanding amounts of not shared with client ivoices and show in report = 1 for non po customers
	not_yet_shared = frappe.db.sql("""
								SELECT 
									customer, 
									SUM(outstanding_amount) as outstanding_amount
								FROM 
									`tabSales Invoice`
								WHERE 
									customer IN ({}) 
									AND (
											(docstatus = 0 AND show_in_report = 1 AND custom_not_for_tracker = 0) 
											OR (docstatus = 1 AND is_shared_with_client = 0 AND custom_not_for_tracker = 0)
										)
								GROUP BY 
									customer
								""".format(', '.join(['%s']*len(customers))), tuple([customer['name'] for customer in customers]), as_dict=True)

	for customer in customers:
		customer['shared_with_client'] = 0
		for shared in shared_with_clients:
			if customer['name'] == shared['customer']:
				customer['shared_with_client'] = shared['outstanding_amount']
		customer['without_po'] = 0
		customer['uploaded_on_client'] = 0
		customer['not_yet_shared'] = 0		
		for not_shared in not_yet_shared:
			if customer['name'] == not_shared['customer']:
				customer['not_yet_shared'] = not_shared['outstanding_amount']

	# PO customers Misk(PROJ-0001), Acwa Neom(PROJ-0002), Acwa Power(PROJ-0013) and Nomac(PROJ-0012)
	# Fetch submitted outstanding amounts of shared with client for po customers
	po_shared_with_clients = frappe.get_all('Sales Invoice',
										 filters={'customer': ('in', [customer['name'] for customer in po_customers]),
												  'docstatus': 1, 'is_shared_with_client': 1, 'custom_not_for_tracker': 0,
												  'po_no': ('!=', '')},
										 fields=['customer', 'sum(outstanding_amount) as outstanding_amount'],
										 group_by='customer')
	# Fetch outstanding amounts of without po invoices of po customer
	without_po = frappe.db.sql("""
								SELECT 
									customer, 
									SUM(outstanding_amount) as outstanding_amount
								FROM 
									`tabSales Invoice`
								WHERE 
									customer IN ({}) 
									AND (docstatus = 0 AND show_in_report = 1 AND po_no = "" AND custom_not_for_tracker = 0)
								GROUP BY 
									customer
								""".format(', '.join(['%s']*len(po_customers))), tuple([customer['name'] for customer in po_customers]), as_dict=True)
	
	# Fetch outstanding amounts of not shared with client ivoices and show in report = 1 for po customers
	po_not_yet_shared = frappe.db.sql("""
								SELECT 
									customer, 
									SUM(outstanding_amount) as outstanding_amount
								FROM 
									`tabSales Invoice`
								WHERE 
									customer IN ({}) 
									AND (
											(docstatus = 0 AND show_in_report = 1 AND po_no != "" AND custom_not_for_tracker = 0) 
											OR (docstatus = 1 AND is_shared_with_client = 0 AND po_no != "" AND custom_not_for_tracker = 0)
										)
								GROUP BY 
									customer
								""".format(', '.join(['%s']*len(po_customers))), tuple([customer['name'] for customer in po_customers]), as_dict=True)

	# Fetch grand total of invoice on which uploaded_on_client = 1
	po_uploaded_with_client = frappe.db.sql("""
								SELECT 
									customer, 
									SUM(outstanding_amount) as outstanding_amount
								FROM 
									`tabSales Invoice`
								WHERE 
									customer IN ({}) 
									AND (docstatus = 1 AND uploaded_on_client_portal = 1 AND custom_not_for_tracker = 0)
								GROUP BY 
									customer
								""".format(', '.join(['%s']*len(po_customers))), tuple([customer['name'] for customer in po_customers]), as_dict=True)


	for customer in po_customers:
		customer['shared_with_client'] = 0
		for shared in po_shared_with_clients:
			if customer['name'] == shared['customer']:
				customer['shared_with_client'] = shared['outstanding_amount']
		
		customer['without_po'] = 0		
		for wp in without_po:
			if customer['name'] == wp['customer']:
				customer['without_po'] = wp['outstanding_amount']

		customer['not_yet_shared'] = 0		
		for not_shared in po_not_yet_shared:
			if customer['name'] == not_shared['customer']:
				customer['not_yet_shared'] = not_shared['outstanding_amount']

		customer['uploaded_on_client'] = 0		
		for up_on in po_uploaded_with_client:
			if customer['name'] == up_on['customer']:
				customer['uploaded_on_client'] = up_on['outstanding_amount']		

		customers.append(customer)

	customers = sorted(customers, key=lambda x: x['project_id'])
	
	for cust in customers:
		if frappe.db.exists("Payment Received No Breakdown",cust['project_id']):
			payment_received_doc = frappe.get_doc("Payment Received No Breakdown", cust['project_id'])
			cust['shared_with_client'] = cust['shared_with_client'] - payment_received_doc.total_received_amount

	return customers