// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
	onload(frm) {
		frm.set_query("customer", function(){
		    return {
		        filters: [
                    ["Customer","is_standard_invoice_customer","=",1]
		        ]
		    }
		});
	},
});