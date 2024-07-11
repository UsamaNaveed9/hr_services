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
	erc_fee: function(frm){
		check_erc_fee(frm);
	},
	before_save: function(frm){
		check_erc_fee(frm);
	}
	
});

function check_erc_fee(frm){
	if(frm.doc.erc_fee < 600){
		frappe.msgprint({
			title: __("Error"),
			indicator: "red",
			message: __("ERC Fee must be greater than 600"),
		});
		frappe.validated = false;
	}
}