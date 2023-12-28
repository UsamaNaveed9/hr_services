// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	setup(frm) {
		frm.set_query("print_customer", function(){
		    return {
		        filters: [
		            ["Customer","project_id","in", frm.doc.project],
                    ["Customer","is_standard_invoice_customer","=",0]
		        ]
		    }
		});
	},
});