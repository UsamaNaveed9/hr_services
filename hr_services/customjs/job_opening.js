// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Opening',{
    refresh(frm){
        if(frm.doc.status == "Open" && cur_frm.doc.__islocal != 1){
            frm.add_custom_button(__('Create Job Applicant'), function(){
                frappe.model.open_mapped_doc({
                    method: "hr_services.custompy.job_opening.create_job_applicant",
                    frm: frm
                });
            }).addClass("btn-primary");
        }
    }
});