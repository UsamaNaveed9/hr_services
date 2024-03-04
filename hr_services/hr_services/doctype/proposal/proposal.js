// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Proposal', {
	setup(frm){
		frm.fields_dict['details'].grid.get_field("costing_sheet").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Costing Sheet', 'sheet_type', '=','ACWA'],
				]
			}
        }
	}
});

frappe.ui.form.on("Proposal Items", {
	costing_sheet: function(frm, cdt, cdn){
		let row = locals[cdt][cdn]
		if(row.costing_sheet){
			frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Costing Sheet",
                    name: row.costing_sheet
                },
                callback(r) {
                    if(r.message) {
                        var d = r.message;
						row.outsourcing_description = d.employee_name;
						let total_salary = 0.0
						total_salary += d.basic + d.housing + d.transport + d.mobile + d.vt_allowance + d.neom_allowance + d.gosi
						let total_yearly_cost = 0.0
						total_yearly_cost += d.yearly_med_inc + d.wl_fee + d.iqama_fee + d.ticket_amount + d.exit_re_entry
						let total_one_time_cost = 0.0
						total_one_time_cost += d.transfer_fee + d.relocation_allowance + d.recruitment_cost
						let total_with_vat = 0.0
						total_with_vat += (total_salary * 12) + total_yearly_cost + total_one_time_cost + d.erc_fee

						row.price_includes_erc_fees_and_without_vat = total_with_vat
						
						frm.refresh();
                    }
                }
            });
		}
	}
});