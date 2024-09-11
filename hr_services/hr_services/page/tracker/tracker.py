import frappe

@frappe.whitelist()
def get_outstanding_customers():
	# Fetch customers according to projects
	customers = frappe.db.sql("""
						SELECT 
							c.name, c.customer_name, c.project_id, p.project_name, p.custom_tracker_order
						FROM 
							`tabCustomer` c
						JOIN 
							`tabProject` p ON c.project_id = p.name
						WHERE 
							c.disabled = 0 
							AND c.is_standard_invoice_customer = 1
						ORDER BY 
							CAST(p.custom_tracker_order AS UNSIGNED) ASC
					""", as_dict=True)

	# Fetch submitted outstanding amounts
	paid_outstanding_amounts = frappe.get_all('Sales Invoice',
										 filters={'customer': ('in', [customer['name'] for customer in customers]),
												  'docstatus': 1, 'custom_not_for_tracker': 0},
										 fields=['customer', 'sum(outstanding_amount) as outstanding_amount'],
										 group_by='customer')
	
	# Fetch draft outstanding amounts
	draft_outstanding_amounts = frappe.get_all('Sales Invoice',
										 filters={'customer': ('in', [customer['name'] for customer in customers]),
												  'docstatus': 0,'show_in_report':1},
										 fields=['customer', 'sum(outstanding_amount) as outstanding_amount'],
										 group_by='customer')

	for customer in customers:
		customer['outstanding_amount'] = 0
		for paid_outstanding_amount in paid_outstanding_amounts:
			if customer['name'] == paid_outstanding_amount['customer']:
				customer['outstanding_amount'] = paid_outstanding_amount['outstanding_amount']
		
		for draft_outstanding_amount in draft_outstanding_amounts:
			if customer['name'] == draft_outstanding_amount['customer']:
				customer['outstanding_amount'] = customer['outstanding_amount'] + draft_outstanding_amount['outstanding_amount']

		if frappe.db.exists("Payment Received No Breakdown",customer['project_id']):
			payment_received_doc = frappe.get_doc("Payment Received No Breakdown", customer['project_id'])
			customer['outstanding_amount'] = customer['outstanding_amount'] - payment_received_doc.total_received_amount

	#Fetch Client employees Total Outstanding of loans except Elite HQ and Loan type: Housing Advance
	query = """
		SELECT
			(SUM(disbursed_amount) - SUM(total_amount_paid)) as total_advance_outstanding
		FROM
			`tabLoan`
		WHERE
			docstatus = 1 
			and loan_type != 'Housing Advance' 
			and applicant IN (
				SELECT
					name
				FROM
					`tabEmployee`
				WHERE
					project != 'PROJ-0018')
			"""

	# Execute the query using frappe.get_all
	client_adv_outstanding = frappe.db.sql(query, as_dict=True)
	
	#Fetch Elite HQ employees Total Outstanding of loans
	query = """
		SELECT
			(SUM(disbursed_amount) - SUM(total_amount_paid)) as total_advance_outstanding
		FROM
			`tabLoan`
		WHERE
			docstatus = 1
			and applicant IN (
				SELECT
					name
				FROM
					`tabEmployee`
				WHERE
					project = 'PROJ-0018')
			"""

	# Execute the query using frappe.get_all
	elite_adv_outstanding = frappe.db.sql(query, as_dict=True)

	return customers,client_adv_outstanding,elite_adv_outstanding