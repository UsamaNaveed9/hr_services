# Copyright (c) 2023, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def check_inv(doc, method):
    if frappe.db.exists("Purchase Invoice",{"supplier": doc.supplier, "bill_no": doc.bill_no}):
        frappe.throw(_("{0} Supplier Invoice No {1} already exist").format(doc.supplier, doc.bill_no))