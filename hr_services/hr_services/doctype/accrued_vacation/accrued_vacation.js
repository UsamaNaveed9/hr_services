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

	return {ms_date: final_start_date, me_date: final_end_date}
}
