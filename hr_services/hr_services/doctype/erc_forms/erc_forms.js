// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('ERC Forms', {
	onload(frm){
		if(frm.doc.__islocal){
			frm.toggle_display(['employee'], false);
			frm.toggle_display(['employee_name'], false);
			frm.toggle_display(['employment_date'], false);
			frm.toggle_display(['nationality'], false);
			frm.toggle_display(['national_id_no'], false);
			frm.toggle_display(['position'], false);
			frm.toggle_display(['project'], false);
			frm.toggle_display(['project_name'], false);
			frm.toggle_display(['last_working_day_date'], false);
			frm.toggle_display(['basic_salary'], false);
			frm.toggle_display(['housing_allowance'], false);
			frm.toggle_display(['year'], false);
			frm.toggle_display(['total_amount'], false);
			frm.toggle_display(['transportation_allowance'], false);
			frm.toggle_display(['vacation_allowance'], false);
			frm.toggle_display(['effective_month'], false);
			frm.toggle_display(['new_basic_salary'], false);
			frm.toggle_display(['monthly_deduction_amount'], false);
			frm.toggle_display(['total_salary'], false);
			frm.toggle_display(['increment'], false);
			frm.toggle_display(['embassy_name_in_arabic'], false);
			frm.toggle_display(['passport_no'], false);
			frm.toggle_display(['items'], false);
			frm.toggle_display(['department'], false);
			frm.toggle_display(['salutation'], false);
			if(frm.doc.date){
				frappe.call({
					method: "hr_services.custompy.employee.convert_into_hijri",
					args: {
						date: frm.doc.date
					},
					callback: function(r){
						if(r.message){
							frm.set_value("date_in_hijri",r.message);
						}
					}
				})
			}
		}
	},
	date(frm){
		frappe.call({
			method: "hr_services.custompy.employee.convert_into_hijri",
			args: {
				date: frm.doc.date
			},
			callback: function(r){
				if(r.message){
					frm.set_value("date_in_hijri",r.message);
				}
			}
		})
	},
	forms(frm){
		show_fields(frm);
	},
	refresh(frm){
		show_fields(frm);
	},
	employee(frm){
		if(frm.doc.forms == 'Experience Letter'){
			frappe.db.get_value("Employee",frm.doc.employee,"relieving_date").then((r)=>{
				if(r.message.relieving_date){
					frm.set_value("last_working_day_date", r.message.relieving_date)
				}
			})
		}
	}
});


function show_fields(frm){
	if(frm.doc.forms == 'Embassy Form'){
		//show fiels
		frm.toggle_display(['embassy_name_in_arabic'], true);
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['nationality'], true);
		frm.toggle_display(['position'], true);
		frm.toggle_display(['passport_no'], true);
		//hide fields
		frm.toggle_display(['salutation'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['national_id_no'], false);
		frm.toggle_display(['project'], false);
		frm.toggle_display(['project_name'], false);
		frm.toggle_display(['employment_date'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['increment'], false);

	}
	else if(frm.doc.forms == 'Employment Letter'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['employment_date'], true);
		frm.toggle_display(['nationality'], true);
		frm.toggle_display(['national_id_no'], true);
		frm.toggle_display(['project'], true);
		frm.toggle_display(['project_name'], true);
		frm.toggle_display(['position'], true);
		//hide fields
		frm.toggle_display(['salutation'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['increment'], false);

	}
	else if(frm.doc.forms == 'End of Contract Notification' || frm.doc.forms == 'Experience Letter'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['employment_date'], true);
		frm.toggle_display(['nationality'], true);
		frm.toggle_display(['national_id_no'], true);
		frm.toggle_display(['project'], true);
		frm.toggle_display(['project_name'], true);
		frm.toggle_display(['position'], true);
		frm.toggle_display(['last_working_day_date'], true);
		//hide fields
		frm.toggle_display(['salutation'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['increment'], false);
	}
	else if(frm.doc.forms == 'ERC Assets Receiving'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['position'], true);
		frm.toggle_display(['items'], true);
		frm.toggle_display(['department'], true);
		//hide fields
		frm.toggle_display(['salutation'], false);
		frm.toggle_display(['employment_date'], false);
		frm.toggle_display(['nationality'], false);
		frm.toggle_display(['national_id_no'], false);
		frm.toggle_display(['project'], false);
		frm.toggle_display(['project_name'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['increment'], false);

		//filter on items
		frm.fields_dict['items'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            // Your condition to filter item codes here
            return {
                filters: [
                    ['Item', 'item_group', '=', 'Assets']
                ]
            };
        };

	}
	else if(frm.doc.forms == 'Indebtedness Letter'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['total_amount'], true);
		frm.toggle_display(['nationality'], true);
		frm.toggle_display(['national_id_no'], true);
		frm.toggle_display(['monthly_deduction_amount'], true);
		frm.toggle_display(['salutation'], true);
		//hide fields
		frm.toggle_display(['position'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['employment_date'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['project'], false);
		frm.toggle_display(['project_name'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['increment'], false);
		
	}
	else if(frm.doc.forms == 'Letter for Extend of Probation'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['position'], true);
		frm.toggle_display(['salutation'], true);
		frm.toggle_display(['employment_date'], true);
		//hide fields
		frm.toggle_display(['nationality'], false);
		frm.toggle_display(['national_id_no'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['basic_salary'], false);
		frm.toggle_display(['housing_allowance'], false);
		frm.toggle_display(['transportation_allowance'], false);
		frm.toggle_display(['vacation_allowance'], false);
		frm.toggle_display(['total_salary'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['project'], false);
		frm.toggle_display(['project_name'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['increment'], false);
	}
	else if(frm.doc.forms == 'Salary Certificate'){
		//show fiels
		frm.toggle_display(['employee'], true);
		frm.toggle_display(['employee_name'], true);
		frm.toggle_display(['employment_date'], true);
		frm.toggle_display(['nationality'], true);
		frm.toggle_display(['national_id_no'], true);
		frm.toggle_display(['position'], true);
		frm.toggle_display(['basic_salary'], true);
		frm.toggle_display(['housing_allowance'], true);
		frm.toggle_display(['transportation_allowance'], true);
		frm.toggle_display(['vacation_allowance'], true);
		frm.toggle_display(['total_salary'], true);
		//hide fields
		frm.toggle_display(['salutation'], false);
		frm.toggle_display(['department'], false);
		frm.toggle_display(['items'], false);
		frm.toggle_display(['passport_no'], false);
		frm.toggle_display(['embassy_name_in_arabic'], false);
		frm.toggle_display(['last_working_day_date'], false);
		frm.toggle_display(['project'], false);
		frm.toggle_display(['project_name'], false);
		frm.toggle_display(['year'], false);
		frm.toggle_display(['total_amount'], false);
		frm.toggle_display(['effective_month'], false);
		frm.toggle_display(['new_basic_salary'], false);
		frm.toggle_display(['monthly_deduction_amount'], false);
		frm.toggle_display(['increment'], false);
	}
	else if(frm.doc.forms == 'Salary Increment Letter'){
		
	}
	else if(frm.doc.forms == 'Salary Letter'){
		
	}
}
