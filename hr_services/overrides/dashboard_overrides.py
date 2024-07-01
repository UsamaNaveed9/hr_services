from frappe import _


def get_dashboard_for_employee(data):
	data["transactions"].extend(
		[
			{"label": _("Purchase Invoice"), "items": ["Purchase Invoice"]},
			{"label": _("Invoice to Client"), "items": ["Sales Invoice"]},
			{"label": _("Employee Advance"), "items": ["Loan"]},
		]
	)

	data["non_standard_fieldnames"].update(
		{"Purchase Invoice": "employee_no", "Sales Invoice": "employee_id", "Loan": "applicant"}
	)
	return data