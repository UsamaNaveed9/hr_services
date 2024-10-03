// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract For Part Timers', {
	setup: function(frm){
		frm.set_query("department", function() {
			return {
				filters: {
					"custom_project":frm.doc.project
				}
			};
		});
	},
	start_date: function(frm){
		calculate_end_date(frm);
	},
	duration_in_months: function(frm){
		calculate_end_date(frm);
	}
});


function calculate_end_date(frm){
    if(frm.doc.start_date && frm.doc.duration_in_months){
		let days = frm.doc.duration_in_months * 30.4167;
        frm.set_value("end_date", frappe.datetime.add_days(frm.doc.start_date, days));
    }   
}