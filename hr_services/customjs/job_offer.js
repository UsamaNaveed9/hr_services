// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.provide("erpnext.job_offer");

frappe.ui.form.on('Job Offer', {
	onload: function (frm) {
		frm.set_query("select_terms", function() {
			return { filters: { custom_for_job_offer: 1 } };
		});

		if(frm.doc.__islocal){
			var new_row = cur_frm.add_child('custom_salary_details');
			new_row.salary_components = 'Basic Salary';
			var new_row = cur_frm.add_child('custom_salary_details');
			new_row.salary_components = 'Housing Allowance';
			var new_row = cur_frm.add_child('custom_salary_details');
			new_row.salary_components = 'Transportations Allowance';
			cur_frm.refresh_field("custom_salary_details");
		}
	},
	before_save(frm){
		if(frm.doc.custom_salary_details){
			calculate_salary(frm);
		}
	},
	refresh: function (frm) {
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			if(frm.doc.custom_nationality == "Saudi"){
				if((frm.doc.custom_qiwa_status == 'Accepted by Candidate' || frm.doc.custom_qiwa_status == 'Accepted by His/Her Sponsor') 
					&& (frm.doc.custom_gosi_status == 'Accepted')){
						frm.add_custom_button(__('Create Employee'),
							function () {
								erpnext.job_offer.make_employee(frm);
							}
						);
				}
			}
			if(frm.doc.custom_nationality == "Non Saudi"){
				if(frm.doc.custom_qiwa_status == 'Accepted by Candidate' || frm.doc.custom_qiwa_status == 'Accepted by His/Her Sponsor'){
					frm.add_custom_button(__('Create Employee'),
						function () {
							erpnext.job_offer.make_employee(frm);
						}
					);
					
				}
			}
		}
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.custom_job_title_on_visa)
			&& (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			frm.add_custom_button(__('Create Contract'),
				function () {
					erpnext.job_offer.make_contract(frm);
				}
			);
		}
		if(frm.doc.custom_project && frm.doc.docstatus == 0){
			if(frm.doc.custom_project == "PROJ-0002"){ //ACWA-NEOM project
				frm.set_value("select_terms","Neom");
			}
			else if(frm.doc.custom_project == "PROJ-0001"){ //Misk project
				frm.set_value("select_terms","Misk");
			}
			else if(frm.doc.custom_project == "PROJ-0005"){ //Cummins project
				frm.set_value("select_terms","Cummins");
			}
			else if(frm.doc.custom_project == "PROJ-0022" && frm.doc.custom_divisions == "Hittin"){ //Riyadh Schools Platform and division == Hittin project
				frm.set_value("select_terms","RSP Hittin");
			}
			else if(frm.doc.custom_project == "PROJ-0022" && frm.doc.custom_divisions == "Admin"){ //Riyadh Schools Platform and division == Admin project
				frm.set_value("select_terms","RSP Admin");
			}
			else if(frm.doc.custom_project == "PROJ-0022" && frm.doc.custom_divisions == "Al-Salam"){ //Riyadh Schools Platform and division == Al-Salam project
				frm.set_value("select_terms","RSP Al-Salam");
			}
			else{
				frm.set_value("select_terms","Elite");
			}
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
	frappe.model.open_mapped_doc({
		method: "hr_services.custompy.job_offer.make_employee",
		frm: frm
	});
};

erpnext.job_offer.make_contract = function (frm) {
	frappe.model.open_mapped_doc({
		method: "hr_services.custompy.job_offer.make_contract",
		frm: frm
	});
};