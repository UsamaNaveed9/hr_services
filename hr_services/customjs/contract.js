// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract',{
    onload(frm){
        if(frm.doc.custom_posting_date && cur_frm.doc.__islocal){
            convert_into_hijri(frm);
        }
    },
    refresh(frm){
        calculate_end_date(frm);
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__('Create Word File'), function (){
                var dialog = new frappe.ui.Dialog({
                    title: __('Choose a template file'),
                    fields: [
                        {
                            fieldname: 'template',
                            fieldtype: 'Link',
                            label: 'Word Template',
                            options: 'Word Template'
                        },
                    ],
                    primary_action: () => {
                        dialog.hide();
                        frappe.call({
                            method: "hr_services.custompy.contract.fill_and_attach_template",
                            args: {
                                doctype: frm.doc.doctype,
                                name: frm.doc.name,
                                template: dialog.get_values().template,
                            },
                            freeze: true,
                            freeze_message: __("Creating Contract Word File......."),
                            callback: (r) => frm.reload_doc(),
                        });
                    }
                });
                dialog.show();
            }).addClass('btn-primary');
        }
        if(frm.doc.is_signed == 1 && frm.doc.docstatus == 1){
            frm.add_custom_button(__('Create Employee'), function(){
                frappe.model.open_mapped_doc({
                    method: "hr_services.custompy.contract.make_employee",
                    frm: frm
                });
            }).addClass('btn-primary');
        }
    },
    custom_posting_date(frm){
        convert_into_hijri(frm);
    },
    is_signed(frm){
        if(frm.doc.is_signed == 1){
            frm.set_value("custom_status", "Signed");
        }
        else if(frm.doc.is_signed == 0){
            frm.set_value("custom_status", "Sent");
        }
    },
    custom_contract_duration(frm){
        calculate_end_date(frm);
    },
    before_save(frm){
		if(frm.doc.salary_detail){
			calculate_salary(frm);
		}
	},
});

function calculate_end_date(frm){
    if(frm.doc.custom_contract_duration == 1){
        let end_date = frappe.datetime.add_days(frm.doc.start_date, 365);
        frm.set_value("end_date", end_date);
    }
    else if(frm.doc.custom_contract_duration == 2){
        let end_date = frappe.datetime.add_days(frm.doc.start_date, 730);
        frm.set_value("end_date", end_date);
    }
}

frappe.ui.form.on("Contract Details", {
	amount:function(frm, cdt, cdn){
		calculate_salary(frm);
	},
	salary_detail_remove(frm,cdt,cdn){
		calculate_salary(frm);
	}
});

function calculate_salary(frm){
    let total = 0;
	for(let i in frm.doc.salary_detail){
		total += frm.doc.salary_detail[i].amount;
	}
	frm.set_value("custom_total_salary", total);
	frm.refresh();
}

function convert_into_hijri(frm){
    frappe.call({
        method: "hr_services.custompy.employee.convert_into_hijri",
        args: {
            date: frm.doc.custom_posting_date
        },
        callback: function(r){
            if(r.message){
                frm.set_value("custom_date_in_hijri",r.message);
            }
        }
    });
}