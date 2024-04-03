// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		//setting the return series if is_return is checked
		if(frm.doc.is_return == 1){
			frm.set_value("naming_series","ACC-SINV-RET-.YYYY.-")
		}
	},
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
	is_return(frm) {
		if(frm.doc.is_return == 1){
			frm.set_value("naming_series","ACC-SINV-RET-.YYYY.-")
		}
		else{
			frm.set_value("naming_series","Draft-.YYYY.-")
		}
	}
});