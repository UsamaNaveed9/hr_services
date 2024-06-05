// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	refresh: function(frm) {
		//setting the return series if is_return is checked
		if(frm.doc.is_return == 1){
			frm.set_value("naming_series","ACC-PINV-RET-.YYYY.-");
		}
	},
	setup(frm) {
		frm.fields_dict['items'].grid.get_field("employee_no").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project],
				]
			}
        }
	},
	is_return(frm) {
		if(frm.doc.is_return == 1){
			frm.set_value("naming_series","ACC-PINV-RET-.YYYY.-");
		}
		else{
			frm.set_value("naming_series","ACC-PINV-.YYYY.-");
		}
	}
});