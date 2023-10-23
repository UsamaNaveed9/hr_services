// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assets Request', {
	refresh: function(frm) {
        frm.fields_dict['items'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            // Your condition to filter item codes here
            return {
                filters: [
                    ['Item', 'item_group', '=', 'Assets']
                ]
            };
        };
    }
})
