// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	setup(frm) {
		frm.fields_dict['items'].grid.get_field("employee_no").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project],
				]
			}
        }
	},
});