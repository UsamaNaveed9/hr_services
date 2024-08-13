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
	before_save: function(frm){
		validate(frm);
	},
	invoice_type: function(frm){
		if(frm.doc.invoice_type == 'Employee Wise Invoices with PO from PO Mgt'){
			frm.set_value("custom_allow_po_management",1);
			frm.set_value("custom_with_po",1);
		}
		else if(frm.doc.invoice_type == 'Employee Wise Invoices without PO from PO Mgt'){
			frm.set_value("custom_allow_po_management",1);
			frm.set_value("custom_with_po",0);
		}
		else{
			frm.set_value("custom_allow_po_management",0);
			frm.set_value("custom_with_po",0);
		}
	}
	
});

function validate(frm){
	if(frm.doc.invoice_type && !frm.doc.customer){
		frappe.msgprint({
			title: __("Error"),
			indicator: "red",
			message: __("Customer is missing"),
		});
		frappe.validated = false;
		frm.scroll_to_field('customer');
	}
	if(!((['Employee Wise Invoices with PO from PO Mgt','Employee Wise Invoices without PO from PO Mgt']).includes(frm.doc.invoice_type))){
		if(frm.doc.erc_fee < 600){
			frappe.msgprint({
				title: __("Error"),
				indicator: "red",
				message: __("ERC Fee must be greater than 600"),
			});
			frappe.validated = false;
		}
		frm.scroll_to_field('erc_fee');
	}
}