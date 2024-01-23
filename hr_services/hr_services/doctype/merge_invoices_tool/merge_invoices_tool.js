// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Merge Invoices Tool', {
	refresh: function(frm) {
        // Hide the Save button
        frm.disable_save();
        // Center-align the button with class 'your-button-class'
        frm.fields_dict['if_data_is_ok_you_can_click_here'].$wrapper.css('text-align', 'center');
        frm.fields_dict['merge_invoices'].$wrapper.css('text-align', 'center');
    },
	setup(frm) {
        frm.set_query("customer", function(){
            return{
                filters:[
                    ["Customer","is_standard_invoice_customer","=", 1]
                ]
            }
        });
        
		frm.fields_dict['sales_invoices'].grid.get_field("sales_invoice").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Sales Invoice', 'customer', 'in', frm.doc.customer],
					['Sales Invoice', 'status', 'in', 'Draft'],
                    ['Sales Invoice', 'is_merged', '=', 0 ],
				]
			}
        }
	},
	merge_invoices: function(frm){
        if(frm.doc.customer && frm.doc.sales_invoices.length >= 2 && frm.doc.due_date){
            frappe.call({
                method: "hr_services.hr_services.doctype.merge_invoices_tool.merge_invoices_tool.merge_invoices",
                args: {
                    due_date: frm.doc.due_date,
                    customer: frm.doc.customer,
                    sales_invoices: frm.doc.sales_invoices
                },
                freeze: true,
                freeze_message: "Invoice Merging in progress......",
                callback: function(res){
                    if (res.message){
                        //console.log(res.message);
                        cur_frm.clear_table("sales_invoices");
                        frm.refresh_field("sales_invoices");
                        frappe.msgprint({
                            title: __('Invoice Created Successfully'),
                            indicator: 'green'
                        });
                    }
                }
            })
        }
        else{
            if(!frm.doc.customer){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Customer is missing')
                });
            }
			else if(!frm.doc.due_date){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Invoice Due Date is missing')
                });
            }
			else if(frm.doc.sales_invoices.length < 2){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Sales Invoices must be two or more then two')
                });
            }	
        }
    }
});
