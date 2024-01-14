// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accrued Vacation', {
	refresh: function(frm){
		let dates = get_dates(frm);
		frm.set_value("ms_date", dates.ms_date);
		frm.set_value("me_date", dates.me_date);
	},
	month_name: function(frm){
		let dates = get_dates(frm);
		frm.set_value("ms_date", dates.ms_date);
		frm.set_value("me_date", dates.me_date);
    },
	enter_year: function(frm){
		let dates = get_dates(frm);
		frm.set_value("ms_date", dates.ms_date);
		frm.set_value("me_date", dates.me_date);
    },
	calculate_accrued_salary: function(frm){
		let dates = get_dates(frm);
		if(frm.doc.ms_date == dates.ms_date && frm.doc.me_date == dates.me_date){
			frappe.call({
				method: "hr_services.hr_services.doctype.accrued_vacation.accrued_vacation.calculate_accrued_salary",
				args: {
					end_date: frm.doc.me_date,
					emp_of: frm.doc.accrued_salary_for
				},
				freeze: true,
				freeze_message: "Calculating Accrued Salary of All Employees...",
				callback: function(res){
					let emps = res.message;
					let total_accrued = 0;
					cur_frm.clear_table("accrued");
					for(let i = 0; i < emps.length; i++){
						total_accrued = total_accrued + emps[i].accrued_vacation_salary;
						let add_emp = frm.add_child("accrued");
						add_emp.employee_id = emps[i].name;
						add_emp.employee_name = emps[i].employee_name;
						add_emp.date_of_joining = emps[i].date_of_joining;
						add_emp.project_id = emps[i].project;
						add_emp.project_name = emps[i].project_name;
						add_emp.basic = emps[i].basic_salary;
						add_emp.housing = emps[i].housing_allowance
						add_emp.transport = emps[i].transport_allowance
						add_emp.allowances = emps[i].food_allowance + emps[i].mobile_allowance;
						add_emp.total_salary = emps[i].ctc;
						add_emp.balance_of_vacation = emps[i].leave_balance;
						add_emp.accrued_vacation_salary = emps[i].accrued_vacation_salary;
						add_emp.diff_in_days = emps[i].diff_days;
						add_emp.leaves_till_now = emps[i].leaves_till_now;
						add_emp.allocated_leaves = emps[i].allocated_leaves;
						add_emp.taken_leaves = emps[i].taken_leaves;
					}
					cur_frm.refresh_field("accrued");
					frm.set_value("total_accrued", total_accrued);
				}
			})
		}
		else{
			if(frm.doc.ms_date != dates.ms_date){
				frappe.msgprint({
					title: __('Error'),
					indicator: 'red',
					message: __('Month Start Date must be the first date of the month')
				})
			}
			else if(frm.doc.me_date != dates.me_date){
				frappe.msgprint({
					title: __('Error'),
					indicator: 'red',
					message: __('Month End Date must be the end date of the month')
				})
			}
		}

	}
});

function get_dates(frm){
	var monthName = frm.doc.month_name;
	if(frm.doc.is_previous_year_entry == 1){
		var currentYear = frm.doc.enter_year;
	}
	else{
		var currentYear = frappe.datetime.get_today().split('-')[0];
	}
        
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

	return {ms_date: final_start_date, me_date: final_end_date}
}
