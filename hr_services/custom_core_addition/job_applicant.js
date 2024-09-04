//In JS file of Job Applicant doctype
//make_dashboard(frm) line is commented
// interview button code commented in create_custom_buttons function

frappe.ui.form.on("Job Applicant", {
	refresh: function(frm) {
		frm.set_query("job_title", function() {
			return {
				filters: {
					'status': 'Open'
				}
			};
		});
		frm.events.create_custom_buttons(frm);
		//frm.events.make_dashboard(frm);
	},

	create_custom_buttons: function(frm) {
		// if (!frm.doc.__islocal && frm.doc.status !== "Rejected" && frm.doc.status !== "Accepted") {
		// 	frm.add_custom_button(__("Interview"), function() {
		// 		frm.events.create_dialog(frm);
		// 	}, __("Create"));
		// }
    }
})