// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('End of Services Calculation', {
	refresh: function(frm) {
        // Hide the Save button
        frm.disable_save();
        // Center-align the button with class 'your-button-class'
        frm.fields_dict['calculate'].$wrapper.css('text-align', 'center');
		frm.fields_dict.calculate.$input.css({
            'width': '150px',     // Set the desired width
            'height': '50px',     // Set the desired height
            'background-color': '#3498db',  // Set the desired background color
            'color': '#ffffff',     // Set the desired text color
			'font-size': '20px'
        });
		frm.fields_dict['end_of_service_amount'].$wrapper.css('text-align', 'center');
		frm.fields_dict['end_of_service_amount'].$wrapper.css('font-size', '20px');
    },
	setup(frm) {
		frm.set_query("employee", function(){
		    return {
		        filters: [
		            ["Employee","relieving_date","is", "set"]
		        ]
		    }
		});
	},
	employee: function(frm) {
		if(frm.doc.date_of_joining && frm.doc.relieving_date){
			frappe.call({
				method: "hr_services.hr_services.doctype.end_of_services_calculation.end_of_services_calculation.get_diff",
				args: {
					startdate: frm.doc.date_of_joining,
					lastdate: frm.doc.relieving_date
				},
				//freeze: true,
				//freeze_message: "Calculating End of Services",
				callback: function(res){
					//console.log(res.message);
					frm.set_value("years", res.message[0]);
					frm.set_value("months", res.message[1]);
					frm.set_value("days", res.message[2]);
					frm.set_value("diff_in_years", res.message[3]);
				}
			})
		}
		else{
            if(!frm.doc.date_of_joining){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Date of joining is missing')
                });
            }
            else if(!frm.doc.relieving_date){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Relieving Date is missing')
                });
            }
		}
	},
	calculate: function(frm) {
		if(frm.doc.diff_in_years > 0 && frm.doc.salary > 0){
			frappe.call({
				method: "hr_services.hr_services.doctype.end_of_services_calculation.end_of_services_calculation.calculate_eos",
				args: {
					reason: frm.doc.end_of_service_reason,
					salary: frm.doc.salary,
					diff_yrs: frm.doc.diff_in_years
				},
				freeze: true,
				freeze_message: "Calculating End of Services",
				callback: function(res){
					//console.log(res.message);
					frm.set_value("end_of_service_amount", res.message);
					// frm.set_value("months", res.message[1]);
					// frm.set_value("days", res.message[2]);
					// frm.set_value("diff_in_years", res.message[3]);
				}
			})
		}
		else{
            if(frm.doc.salary == 0){
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Salary must be greater than 0.0')
                });
            }
		}
	},

});
