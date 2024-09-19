// Copyright (c) 2024, Elite Resources Center
// For license information, please see license.txt

frappe.ui.form.on("Job Requisition", {
	refresh: function(frm) {
		if (frm.doc.status === "Open & Approved") {
			frm.add_custom_button(__('Create Job Applicant'), function(){
                frappe.model.open_mapped_doc({
                    method: "hr_services.custompy.job_requisition.create_job_applicant",
                    frm: frm
                });
            }).addClass("btn-primary");
		}

        $('[data-doctype="Job Opening"]').find("div").hide();
        $('[data-doctype="Job Opening"]').find("button").hide();
        $('[data-doctype="Job Opening"]').find("span").hide();
        $('[data-doctype="Job Applicant"]').find("button").hide();
	}
});