// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('PO Management', {
	onload(frm) {
		if(frm.doc.with_po == 0 && !frm.doc.__islocal){
			frm.toggle_display(['remaining_units'], false);
		}
	},
	setup(frm) {
		//only those project will visible that have the Allow PO Management checked
		frm.set_query("project_no", function(){
		    return {
		        filters: [
		            ["Project","custom_allow_po_management","=", 1]
		        ]
		    }
		});
		//employee filtered on the base of project
		frm.set_query("employee_no", function(){
		    return {
		        filters: [
		            ["Employee","project","in", frm.doc.project_no]
		        ]
		    }
		});
	},
	po_units(frm) {
		if(frm.doc.po_amount && frm.doc.po_units){
			with_po_calculation(frm);
		}
		if(frm.doc.used_units){
			if(frm.doc.po_units >= frm.doc.used_units){
				frm.set_value("remaining_units", frm.doc.po_units - frm.doc.used_units );
			}
			else{
				frappe.msgprint({
					title: __('Error'),
					indicator: 'red',
					message: __('Used Units must be less then or equals to PO Units')
				});
			}
		}
		else{
			frm.set_value("remaining_units", frm.doc.po_units );
		}

		if(frm.doc.remaining_units == 0){
			frm.set_value("status", "Completed");
		}
	},
	used_units(frm) {
		if(frm.doc.po_units >= frm.doc.used_units){
			frm.set_value("remaining_units", frm.doc.po_units - frm.doc.used_units );
		}
		else{
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Used Units must be less then or equals to PO Units')
			});
		}

		if(frm.doc.remaining_units == 0){
			frm.set_value("status", "Completed");
		}
	},
	po_amount(frm) {
		if(frm.doc.po_amount && frm.doc.po_units){
			with_po_calculation(frm);
		}
	},
	monthly_amount(frm){
		if(frm.doc.monthly_amount){
			without_po_calculation(frm);
		}
	}
});

function with_po_calculation(frm){
	//inv_rate for invoicing rate, amount_wm for PO Amount without Margin, margin for Margin 8%, emp_rate for Employee Rate
	let inv_rate = 0;
	let amount_wm = 0;
	let margin = 0;
	let emp_rate = 0;
	inv_rate = frm.doc.po_amount / frm.doc.po_units;
	amount_wm = frm.doc.po_amount / 1.08;
	margin = amount_wm * 0.08;
	emp_rate = amount_wm / frm.doc.po_units
	frm.set_value("invoicing_rate",inv_rate);
	frm.set_value("margin",margin);
	frm.set_value("po_amount_wm",amount_wm);
	if(frm.doc.po_type == "Manpower" && frm.doc.employment_type == "Part-time"){
		frm.set_value("employee_rate",emp_rate);
	}
	else if(frm.doc.po_type == "Expense"){
		frm.set_value("employee_rate",inv_rate);
		frm.set_value("invoicing_rate",inv_rate);
		frm.set_value("margin",0);
		frm.set_value("po_amount_wm",frm.doc.po_amount);
	}
	else{
		frm.set_value("employee_rate", 0);
	}
};

function without_po_calculation(frm){
	//inv_rate for invoicing rate, amount_wm for PO Amount without Margin, margin for Margin 8%, emp_rate for Employee Rate
	let inv_rate = 0;
	let amount_wm = 0;
	let margin = 0;
	inv_rate = frm.doc.monthly_amount / 30;
	amount_wm = frm.doc.monthly_amount / 1.08;
	margin = amount_wm * 0.08;
	frm.set_value("invoicing_rate",inv_rate);
	frm.set_value("margin",margin);
	frm.set_value("po_amount_wm",amount_wm);
};
