// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Entry', {
    custom_get_totals: function(frm){
        frappe.call({
            method: "hr_services.custompy.payroll_entry.get_totals",
            args: {
                self: frm.doc
            },
            freeze: true,
            freeze_message: "Getting Totals...",
            callback: function(r){
                let totals = r.message[0];
                //console.log(totals);
                if(totals.total_gross){
                    frm.set_value("custom_total_earnings", totals.total_gross);
                }
                if(totals.total_deduction){
                    frm.set_value("custom_total_deductions", totals.total_deduction + totals.total_loan_repayment);
                }
                if(totals.total_net_pay){
                    frm.set_value("custom_total_net_pay", totals.total_net_pay);
                }
            }
        })
    },
    refresh: function(frm){
        if(frm.doc.docstatus === 1 && frm.doc.workflow_state == "Pending for HRM Approval"){
            frm.add_custom_button(__("Update Payroll"), function() {
                frappe.call({
                    method: "hr_services.custompy.payroll_entry.create_delete_salary_slip",
                    args: {
                        payroll_name: frm.doc.name
                    },
                    callback: function() { }
                });
            }).addClass('btn-primary');
        }
    }
});