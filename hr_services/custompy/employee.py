# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def update_salary(doc, method):
	if frappe.db.exists("Salary Structure Assignment",{"employee": doc.name, "project": doc.project, "company": doc.company}):
		struct_assigned = frappe.get_doc("Salary Structure Assignment", {"employee": doc.name, "project": doc.project, "company": doc.company})
		
		if struct_assigned.base != doc.basic_salary:
			frappe.db.sql("""update `tabSalary Structure Assignment` set base=%s where name=%s """,(doc.basic_salary, struct_assigned.name))
		if struct_assigned.housing_allowance != doc.housing_allowance:
			frappe.db.sql("""update `tabSalary Structure Assignment` set housing_allowance=%s where name=%s """,(doc.housing_allowance, struct_assigned.name))
		if struct_assigned.transport_allowance != doc.transport_allowance:
			frappe.db.sql("""update `tabSalary Structure Assignment` set transport_allowance=%s where name=%s """,(doc.transport_allowance, struct_assigned.name))
		if struct_assigned.food_allowance != doc.food_allowance:
			frappe.db.sql("""update `tabSalary Structure Assignment` set food_allowance=%s where name=%s """,(doc.food_allowance, struct_assigned.name))
		if struct_assigned.mobile_allowance != doc.mobile_allowance:
			frappe.db.sql("""update `tabSalary Structure Assignment` set mobile_allowance=%s where name=%s """,(doc.mobile_allowance, struct_assigned.name))

		frappe.db.commit()

	if doc.iqama_national_id and frappe.db.exists("Employee",{"iqama_national_id": doc.iqama_national_id, "name": ["!=", doc.name]}):
		frappe.throw(_("Iqama No/National ID must be Unique. This <b>{0}</b> is already assigned to another Employee").format(doc.iqama_national_id))	

@frappe.whitelist()
def check_id(doc, method):
	if doc.iqama_national_id and frappe.db.exists("Employee",{"iqama_national_id": doc.iqama_national_id}):
		frappe.throw(_("Iqama No/National ID must be Unique. This <b>{0}</b> is already assigned to another Employee").format(doc.iqama_national_id))


