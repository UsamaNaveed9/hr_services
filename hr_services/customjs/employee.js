
frappe.ui.form.on('Employee', {
    setup(frm) {
		frm.set_query("print_customer_for_invoice", function(){
		    return {
		        filters: [
		            ["Customer","project_id","in", frm.doc.project],
                    ["Customer","is_standard_invoice_customer","=",0]
		        ]
		    }
		});
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

