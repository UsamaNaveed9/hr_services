def get_data():
	return {
		"fieldname": "payroll_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
			"Sales Invoice": "custom_request_for_payment",
			"Payment Entry": "custom_request_for_payment",
			"Loan": "custom_request_for_payment",
		},
		"transactions": [{"items": ["Sales Invoice"]},
				         {"items": ["Journal Entry"]},
						 {"items": ["Payment Entry"]},
						 {"items": ["Loan"]}],
	}