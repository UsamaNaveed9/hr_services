// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Share Payslips via Email', {
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
		//Hide add row button of child table
		frm.set_df_property('employees', 'cannot_add_rows', true);
        // Center-align the button with class 'your-button-class'
        frm.fields_dict['if_data_is_ok_you_can_click_here'].$wrapper.css('text-align', 'center');
        frm.fields_dict['send_emails'].$wrapper.css('text-align', 'center');

        $('[class="control-input"]').find("button").addClass('btn-primary');
        $('[class="control-input"]').find("button").css({'height': '40px','font-weight': '500'});

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
    get_employees: function(frm){
        var project = frm.doc.project;
        if (frm.doc.project && frm.doc.ms_date && frm.doc.me_date){
            frappe.call({
                method: "hr_services.hr_services.doctype.share_payslips_via_email.share_payslips_via_email.get_employees",
                args: {
                    project: project,
                    start_date: frm.doc.ms_date,
                    end_date: frm.doc.me_date
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
							emp_list.email = emp[i].personal_email;
                        }
                        frm.refresh_field("employees");
                    }
                    else{
                        frm.set_value("no_of_employees", res.message.length);
                        cur_frm.clear_table("employees");
                        frm.refresh_field("employees");
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
    send_emails: function(frm){
		frm.doc.employees.forEach(function (row){
			if(!row.email){
				frappe.throw(
					__("<b>Row: {0}</b> Email Address is missing <br> Add <b> Personal Email</b> of Employee in the Employee List <b>OR</b> Delete row from the table", [row.idx])
				);
			}
		})
        if(frm.doc.employees.length > 0){
            frappe.call({
                method: "hr_services.hr_services.doctype.share_payslips_via_email.share_payslips_via_email.send_emails",
                args: {
                    employees: frm.doc.employees,
					month_name: frm.doc.month_name,
					year: frm.doc.year
                },
                freeze: true,
                freeze_message: "Payslips via emails are sending......",
                callback: function(res){
                    if (res.message){
                        //console.log(res.message);
                        cur_frm.clear_table("employees");
                        frm.refresh_field("employees");
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Emails Sent Successfully :)')
                        });
                    }
                }
            })
        }
        else{
            if(frm.doc.employees.length == 0){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Employees are missing')
                });
            }
        }
    }
});
