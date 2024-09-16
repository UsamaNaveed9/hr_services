
frappe.ui.form.on("Job Applicant", {
	refresh: function(frm) {
		$('[data-doctype="Employee"]').find("button").hide();
        $('[data-doctype="Contract"]').find("button").hide();
        $('[data-doctype="Job Offer"]').find("button").hide();
		$('[data-label="View"]').find("button").addClass('btn-primary');
		$('[data-label="Create"]').find("button").addClass('btn-primary');
	}
})