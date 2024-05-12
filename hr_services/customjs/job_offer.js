// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.provide("erpnext.job_offer");

frappe.ui.form.on('Job Offer', {
	before_save(frm){
		if(frm.doc.custom_salary_details){
			calculate_salary(frm);
		}
	},
	refresh: function (frm) {
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.custom_qiwa_status == 'Accepted by Candidate' || frm.doc.custom_qiwa_status == 'Accepted by His/Her Sponsor') 
			&& (frm.doc.custom_gosi_status == 'Accepted') && (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			frm.add_custom_button(__('Create Employee'),
				function () {
					erpnext.job_offer.make_employee(frm);
				}
			);
		}
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.custom_job_title_on_visa)
			&& (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			frm.add_custom_button(__('Create Contract'),
				function () {
					erpnext.job_offer.make_contract(frm);
				}
			);
		}

	},
	custom_nationality: function(frm) {
		if(frm.doc.custom_nationality == 'Saudi'){
			frm.set_value("custom_country", "Saudi Arabia");
		}
		else{
			frm.set_value("custom_country", "");
		}
	},
	custom_applicant_type: function(frm){
		if(frm.doc.custom_applicant_type == 'Local'){
			frm.set_value("custom_job_title_on_visa", "");
		}
		else if(frm.doc.custom_applicant_type == 'Overseas'){
			frm.set_value("custom_qiwa_status", "");
			frm.set_value("custom_gosi_status", "");
		}
		else{
			frm.set_value("custom_qiwa_status", "");
			frm.set_value("custom_gosi_status", "");
			frm.set_value("custom_job_title_on_visa", "");
		}
	}
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

erpnext.job_offer.make_employee = function (frm) {
	console.log("YES")
	frappe.model.open_mapped_doc({
		method: "hr_services.custompy.job_offer.make_employee",
		frm: frm
	});
};