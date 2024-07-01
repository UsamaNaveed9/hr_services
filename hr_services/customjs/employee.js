
frappe.ui.form.on('Employee', {
    onload: function (frm) {
		frm.set_query("department", function() {
			return {
				"filters": {
					"company": frm.doc.company,
                    "custom_project": frm.doc.project,
				}
			};
		});
	},
    setup(frm) {
		frm.set_query("print_customer_for_invoice", function(){
		    return {
		        filters: [
		            ["Customer","project_id","in", frm.doc.project],
                    ["Customer","is_standard_invoice_customer","=",0]
		        ]
		    }
		});

        frm.set_query("custom_bank", function(){
		    return {
		        filters: {
                    custom_show_in_emp_master: 1
                }
		    }
		});

        if(frm.doc.project){
            frm.set_query("custom_class", function (doc) {
                return {
                  query:"hr_services.custompy.employee.get_classes",
                  filters: {
                    value: frm.doc.project,
                    apply_on: frm.doc.project_name,
                  },
                };
            });
        }
	},
	basic_salary(frm) {
		calculate_ctc(frm);
	},
    housing_allowance(frm){
        calculate_ctc(frm);
    },
    transport_allowance(frm){
        calculate_ctc(frm);
    },
    food_allowance(frm){
        calculate_ctc(frm);
    },
    mobile_allowance(frm){
        calculate_ctc(frm);
    },
    iqama_issue_date(frm){
        if(frm.doc.iqama_issue_date){
            frappe.call({
                method: "hr_services.custompy.employee.convert_into_hijri",
                args: {
                    date: frm.doc.iqama_issue_date
                },
                callback: function(r){
                    if(r.message){
                        frm.set_value("custom_iqama_issue_date_in_hijri",r.message);
                    }
                }
            })
        }
    },
    iqama_expiry_date(frm){
        if(frm.doc.iqama_expiry_date){
            frappe.call({
                method: "hr_services.custompy.employee.convert_into_hijri",
                args: {
                    date: frm.doc.iqama_expiry_date
                },
                callback: function(r){
                    if(r.message){
                        frm.set_value("custom_iqama_expiry_date_in_hijri",r.message);
                    }
                }
            })
        }
    },
    custom_h_i_cancelled(frm){
        if(frm.doc.custom_h_i_cancelled == 1){
            frm.set_value("custom_hi_cancelled_status","Yes");
        }
        else{
            frm.set_value("custom_hi_cancelled_status","");
        }
    },
    custom_clearance_form_signed(frm){
        if(frm.doc.custom_clearance_form_signed == 1){
            frm.set_value("custom_cf_signed_status","Yes");
        }
        else{
            frm.set_value("custom_cf_signed_status","");
        }
    },
    custom_gosi_removed(frm){
        if(frm.doc.custom_gosi_removed == 1){
            frm.set_value("custom_gosi_removed_status","Yes");
        }
        else{
            frm.set_value("custom_gosi_removed_status","");
        }
    },
    date_of_joining(frm){
        calculate_probation_end_date(frm);
    },
    custom_probation_period(frm){
        calculate_probation_end_date(frm);
    },
    before_save(frm){
        if(frm.doc.custom_residence_type == "Visitor(Have Border No)"){
            if (frm.doc.iqama_national_id.length != 10 || frm.doc.iqama_national_id[0] != '3'){ //border no length must be 10 and start with 3
                frappe.msgprint({
                    title: __("Error"),
                    indicator: "red",
                    message: __("Enter a valid Border No"),
                });
                frappe.validated = false;
            }
        }
        else if(frm.doc.custom_residence_type == "Resident(Have ID/Iqama No)"){
            if (frm.doc.nationality == "Saudi Arabia" && (frm.doc.iqama_national_id.length != 10 || frm.doc.iqama_national_id[0] != '1')){ //saudi national id length must be 10 and start with 1
                frappe.msgprint({
                    title: __("Error"),
                    indicator: "red",
                    message: __("Enter a valid National ID"),
                });
                frappe.validated = false;
            }
            else if (frm.doc.nationality != "Saudi Arabia" && (frm.doc.iqama_national_id.length != 10 || frm.doc.iqama_national_id[0] != '2')){ //iqama no length must be 10 and start with 2
                frappe.msgprint({
                    title: __("Error"),
                    indicator: "red",
                    message: __("Enter a valid Iqama No"),
                });
                frappe.validated = false;
            }
        }

        //limit on iban must be 24. if bank is alinma then add amount no with limit 14
        if(frm.doc.bank_name){
            // Regular expression to check for any letter (a-z, A-Z)
            const letterRegex = /[a-zA-Z]/;

            // Test the IBAN string against the regular expression
            let letterExist = letterRegex.test(frm.doc.iban);
            
            if(frm.doc.bank_name == "INMA" && (frm.doc.iban.length != 14 || letterExist)){
                frappe.msgprint({
                    title: __("Error"),
                    indicator: "red",
                    message: __("Enter a valid Account No"),
                });
                frappe.validated = false;
            }
            else if(frm.doc.bank_name != "INMA" && (frm.doc.iban.length != 24 || !letterExist)){
                frappe.msgprint({
                    title: __("Error"),
                    indicator: "red",
                    message: __("Enter a valid IBAN"),
                });
                frappe.validated = false;
            }
        }
    }
});

function calculate_ctc(frm){
    let total_salary = 0
        if(frm.doc.basic_salary){
            total_salary = total_salary + frm.doc.basic_salary;
        }
        if(frm.doc.housing_allowance){
            total_salary = total_salary + frm.doc.housing_allowance;
        }
        if(frm.doc.transport_allowance){
            total_salary = total_salary + frm.doc.transport_allowance;
        }
        if(frm.doc.food_allowance){
            total_salary = total_salary + frm.doc.food_allowance;
        }
        if(frm.doc.mobile_allowance){
            total_salary = total_salary + frm.doc.mobile_allowance;
        }

        frm.set_value("ctc", total_salary);
}

function calculate_probation_end_date(frm){
    if(frm.doc.date_of_joining && frm.doc.custom_probation_period){
        frm.set_value("custom_probation_end_date", frappe.datetime.add_days(frm.doc.date_of_joining, frm.doc.custom_probation_period - 1));
    }   
}