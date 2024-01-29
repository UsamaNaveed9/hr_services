// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	// refresh: function(frm) {
	// 	// Add a custom query to filter customers
	// 	frm.fields_dict['customer'].get_query = function(doc, cdt, cdn) {
	// 		return {
	// 			filters: {
	// 				'is_standard_invoice_customer': 1
	// 			}
	// 		};
	// 	};
	// },
	setup(frm) {
		frm.set_query("customer", function(){
            return{
                filters: [
                    ["Customer","is_standard_invoice_customer","=", 1],
                ]
            }
        });

		frm.set_query("print_customer", function(){
		    return {
		        filters: [
		            ["Customer","project_id","in", frm.doc.project],
                    ["Customer","is_standard_invoice_customer","=",0]
		        ]
		    }
		});

		frm.fields_dict['items'].grid.get_field("employee_id").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project],
				]
			}
        }
	},
});