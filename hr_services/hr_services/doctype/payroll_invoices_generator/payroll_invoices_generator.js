// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Invoices Generator', {
    onload: function(frm){
        // Get the current month name
        var monthNames = ["January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"];
        var currentDate = new Date();
        var currentMonth = monthNames[currentDate.getMonth()];

        // Set the field value with the current month name
        frm.set_value('month_name', currentMonth);
    },
	refresh: function(frm) {
        // Hide the Save button
        frm.disable_save();
        // Center-align the button with class 'your-button-class'
        frm.fields_dict['if_data_is_ok_you_can_click_here'].$wrapper.css('text-align', 'center');
        frm.fields_dict['generate_invoices'].$wrapper.css('text-align', 'center');
    },
    month_name: function(frm){
        var monthName = frm.doc.month_name;
        var currentYear = frappe.datetime.get_today().split('-')[0];
        
        // Convert month name to a numeric value
        const monthIndex = new Date(`${monthName} 1, ${currentYear}`).getMonth();

        // Calculate the start date of the month
        const startDate = new Date(currentYear, monthIndex, 1);

        // Calculate the end date of the month
        const endDate = new Date(currentYear, monthIndex + 1, 0);

        // Return the formatted dates
        let start = startDate.toISOString().split('T')[0];
        let end = endDate.toISOString().split('T')[0];
        let final_start_date = frappe.datetime.add_days(start, 1)
        let final_end_date = frappe.datetime.add_days(end, 1)

        frm.set_value("ms_date", final_start_date);
        frm.set_value("me_date", final_end_date);
        frm.set_value("year", currentYear);
    },
    project: function(frm){
        //When Project is Misk then Employment Type set from here
        if(frm.doc.project == "PROJ-0001"){
            frm.set_value("employment_type", "Full-time");
        }
    },
    get_employees: function(frm){
        var project = frm.doc.project;
        if (frm.doc.allow_po_management == 0 && frm.doc.ms_date && frm.doc.me_date){
            frappe.call({
                method: "hr_services.hr_services.doctype.payroll_invoices_generator.payroll_invoices_generator.get_employees",
                args: {
                    project: project,
                    start_date: frm.doc.ms_date,
                    end_date: frm.doc.me_date,
                    month_name: frm.doc.month_name
                },
                freeze: true,
                freeze_message: "Getting Employees...",
                callback: function(res){
                    //console.log(res.message);
                    if (res.message.length > 0){
                        let emp = res.message;
                        frm.set_value("no_of_employees", res.message.length);
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
                        frm.set_value("no_of_employees", res.message.length);
                        cur_frm.clear_table("employees");
                        frm.refresh_field("employees");
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('Invoices already Created!')
                        });
                    }
                }
            })
        }
        else if (frm.doc.allow_po_management == 1 && frm.doc.ms_date && frm.doc.me_date){
            frappe.call({
                method: "hr_services.hr_services.doctype.payroll_invoices_generator.payroll_invoices_generator.get_allow_po_mgt_employees",
                args: {
                    project: project,
                    start_date: frm.doc.ms_date,
                    end_date: frm.doc.me_date,
                    type: frm.doc.employment_type
                },
                freeze: true,
                freeze_message: "Getting Employees",
                callback: function(res){
                    //console.log(res.message);
                    if (res.message.length > 0){
                        let emp = res.message;
                        frm.set_value("no_of_employees", res.message.length);
                        cur_frm.clear_table("employees");
                        for (let i=0;i < emp.length; i++){
                            let emp_list = frm.add_child("employees");
                            emp_list.employee = emp[i].name;
                            emp_list.employee_name = emp[i].employee_name;
                            emp_list.salary_slip = emp[i].salary_slip;
                            emp_list.total_remaining_units = emp[i].remaining_units;
                        }
                        frm.refresh_field("employees");
                    }
                    else if(res.message.length == 0){
                        frm.set_value("no_of_employees", res.message.length);
                        cur_frm.clear_table("employees");
                        frm.refresh_field("employees");
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('Invoices already Created!')
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
            else if(!frm.doc.employment_type){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Employment Type is missing')
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
                    employees: frm.doc.employees,
                    month_name: frm.doc.month_name,
                    my_in_arabic: frm.doc.my_in_arabic,
                    year: frm.doc.year
                },
                freeze: true,
                freeze_message: "Invoice Creation in progress......",
                callback: function(res){
                    if (res.message){
                        //console.log(res.message);
                        cur_frm.clear_table("employees");
                        frm.refresh_field("employees");
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Invoice Created Successfully :)')
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

frappe.ui.form.on("Employees Payroll IG", {
    working_days: function(frm,cdt,cdn){
        let row = locals[cdt][cdn];
        if(row.working_days > row.total_remaining_units && frm.doc.with_po == 1){
            row.working_days = 0;
            frm.refresh_field("employees");
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: __('Working Days not greater than Total Remaining Units')
            });
        }
    }
});