
import frappe

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


