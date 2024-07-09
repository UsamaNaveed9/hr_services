
//Create Employee button code commented on the refresh event of job offer
//Below is the updated code

frappe.ui.form.on("Job Offer", {
	refresh: function (frm) {
		// if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted')
		// 	&& (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
		// 	frm.add_custom_button(__('Create Employee'),
		// 		function () {
		// 			erpnext.job_offer.make_employee(frm);
		// 		}
		// 	);
		// }

		if(frm.doc.__onload && frm.doc.__onload.employee) {
			frm.add_custom_button(__('Show Employee'),
				function () {
					frappe.set_route("Form", "Employee", frm.doc.__onload.employee);
				}
			);
		}
	}

});