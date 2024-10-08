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
			new_row.amount = 0.0;
			var new_row = cur_frm.add_child('custom_salary_details');
			new_row.salary_components = 'Housing Allowance';
			new_row.amount = 0.0;
			var new_row = cur_frm.add_child('custom_salary_details');
			new_row.salary_components = 'Transportations Allowance';
			new_row.amount = 0.0;
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
						).addClass('btn-primary');;
				}
			}
			if(frm.doc.custom_nationality == "Non Saudi"){
				if(frm.doc.custom_qiwa_status == 'Accepted by Candidate' || frm.doc.custom_qiwa_status == 'Accepted by His/Her Sponsor'){
					frm.add_custom_button(__('Create Employee'),
						function () {
							erpnext.job_offer.make_employee(frm);
						}
					).addClass('btn-primary');;
					
				}
			}
		}
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.custom_job_title_on_visa)
			&& (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			frm.add_custom_button(__('Create Contract'),
				function () {
					erpnext.job_offer.make_contract(frm);
				}
			).addClass('btn-primary');
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
		else if(frm.doc.custom_nationality == 'Non Saudi'){
			frappe.call({
				'method': 'frappe.client.get_value',
				'args': {
					'doctype': 'Job Applicant',
					'filters': {
						'name': frm.doc.job_applicant
					},
				   'fieldname':'custom_nationality'
				},
				'callback': function(res){
					frm.set_value("custom_country",res.message.custom_nationality);
				}
			});
		}
		else{
			frm.set_value("custom_country", "");
		}
	},
	custom_applicant_type: function(frm){
		if(frm.doc.custom_applicant_type == 'Local'){
			frm.set_value("custom_job_title_on_visa", "");
			frm.set_value("custom_nationality", "");
			frm.set_df_property('custom_nationality','read_only',0);
		}
		else if(frm.doc.custom_applicant_type == 'Overseas'){
			frm.set_value("custom_qiwa_status", "");
			frm.set_value("custom_gosi_status", "");
			frm.set_value("custom_nationality", "Non Saudi");
			frm.set_df_property('custom_nationality','read_only',1);
			frappe.call({
				'method': 'frappe.client.get_value',
				'args': {
					'doctype': 'Job Applicant',
					'filters': {
						'name': frm.doc.job_applicant
					},
				   'fieldname':'custom_nationality'
				},
				'callback': function(res){
					frm.set_value("custom_country",res.message.custom_nationality);
				}
			});
		}
		else{
			frm.set_value("custom_qiwa_status", "");
			frm.set_value("custom_gosi_status", "");
			frm.set_value("custom_job_title_on_visa", "");
			frm.set_value("custom_nationality", "");
			frm.set_df_property('custom_nationality','read_only',0);
		}
	},
	offer_date: function(frm){
		convert_into_hijri(frm);
	},
	select_terms: function (frm) {
		if(frm.doc.select_terms){
			frappe.call({
				method: 'hr_services.custompy.job_offer.get_terms_and_conditions',
				args: {
					template_name: frm.doc.select_terms,
					doc: frm.doc
				},
				callback: function(r) {
					if (!r.exc) {
						frm.set_value("custom_terms_and_conditions_in_arabic", r.message);
					}
				}
			})
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

function convert_into_hijri(frm){
    frappe.call({
        method: "hr_services.custompy.employee.convert_into_hijri",
        args: {
            date: frm.doc.offer_date
        },
        callback: function(r){
            if(r.message){
                frm.set_value("custom_offer_date_in_hijri",r.message);
            }
        }
    });
}