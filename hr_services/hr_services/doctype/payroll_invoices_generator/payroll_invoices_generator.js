// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Invoices Generator', {
	refresh: function(frm) {
        // Center-align the button with class 'your-button-class'
        frm.fields_dict['if_data_is_ok_you_can_click_here'].$wrapper.css('text-align', 'center');
        frm.fields_dict['generate_invoices'].$wrapper.css('text-align', 'center');
    },
    get_employees: function(frm){
        var project = frm.doc.project;
        if (project && frm.doc.ms_date && frm.doc.me_date){
            frappe.call({
                method: "hr_services.hr_services.doctype.payroll_invoices_generator.payroll_invoices_generator.get_employees",
                args: {
                    project: project,
                    start_date: frm.doc.ms_date,
                    end_date: frm.doc.me_date
                },
                freeze: true,
                freeze_message: "Getting Employees",
                callback: function(res){
                    //console.log(res.message);
                    if (res.message.length > 0){
                        let emp = res.message;
                        cur_frm.clear_table("employees");
                        for (let i=0;i < emp.length; i++){
                            let emp_list = frm.add_child("employees");
                            emp_list.employee = emp[i].name;
                            emp_list.employee_name = emp[i].employee_name;
                            emp_list.salary_slip = emp[i].salary_slip;
                        }
                        frm.refresh_field("employees");
                    }
                    else if(res.message.length == 0){
                        frappe.msgprint({
                            title: __('Notification'),
                            indicator: 'green',
                            message: __('All Employees Invoice Created')
                        });
                    }
                }
            })
        }
        else{
            if(!frm.doc.project){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Project is missing')
                });
            }
            else if(!frm.doc.ms_date){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Month Start Date is missing')
                });
            }
            else if(!frm.doc.me_date){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Month End Date is missing')
                });
            }
            
        }
    },
    generate_invoices: function(frm){
        if(frm.doc.due_date && frm.doc.employees.length > 0){
            frappe.call({
                method: "hr_services.hr_services.doctype.payroll_invoices_generator.payroll_invoices_generator.generate_invoices",
                args: {
                    project: frm.doc.project,
                    due_date: frm.doc.due_date,
                    customer: frm.doc.customer,
                    invoice_type: frm.doc.invoice_type,
                    employees: frm.doc.employees
                },
                freeze: true,
                freeze_message: "Invoice Creation in progress",
                callback: function(res){
                    if (res.message){
                        //console.log(res.message);
                        cur_frm.clear_table("employees");
                        frm.save()
                        frappe.msgprint({
                            title: __('Invoice Created Successfully'),
                            indicator: 'green'
                        });
                    }
                }
            })
        }
        else{
            if(!frm.doc.due_date){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Invoice Due Date is missing')
                });
            }
            else if(frm.doc.employees.length == 0){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Employees are missing')
                });
            }
        }
    }
});
