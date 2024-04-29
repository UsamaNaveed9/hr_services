// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Offer', {
	before_save(frm){
		if(frm.doc.custom_salary_details.length > 0){
			calculate_salary(frm);
		}
	},
});

frappe.ui.form.on("Contract Details", {
	amount:function(frm, cdt, cdn){
		calculate_salary(frm);
	},
	custom_salary_details_remove(frm,cdt,cdn){
		calculate_salary(frm);
	}
});

function calculate_salary(frm){
    let total = 0;
	for(let i in frm.doc.custom_salary_details){
		total += frm.doc.custom_salary_details[i].amount;
	}
	frm.set_value("custom_total_salary", total);
	frm.refresh();
}