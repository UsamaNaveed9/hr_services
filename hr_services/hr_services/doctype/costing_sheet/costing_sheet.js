// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Costing Sheet', {
	onload: function(frm){
		if(frm.is_new()){
			frm.set_value("transfer_fee",2000);
			frm.set_value("transaction_fee",5);
			frm.set_value("iqama_fee",650);
			frm.set_value("wl_fee",9700);
			frm.set_value("exit_re_entry",200);
		}
	},
	employee_id: function(frm) {
		if(frm.doc.employee_id){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					name: frm.doc.employee_id,
				},
				callback(r) {
					if(r.message) {
						var d = r.message;
						//console.log(d);
						frm.set_value("employee_name", d.employee_name);
						frm.set_value("id_or_iqama", d.iqama_national_id);
						frm.set_value("nationality", d.nationality);
						frm.set_value("job_title", d.designation);
						frm.set_value("basic", d.basic_salary);
						frm.set_value("housing", d.housing_allowance);
						frm.set_value("transport", d.transport_allowance);
						frm.set_value("mobile", d.mobile_allowance);
						frm.set_value("food", d.food_allowance);
						let total_salry = (d.basic_salary + d.housing_allowance + d.transport_allowance + d.mobile_allowance + d.food_allowance);
						frm.set_value("total_salary", total_salry);
						if(frm.doc.nationality == "Saudi Arabia"){
							frm.set_value("gosi", (d.basic_salary + d.housing_allowance) * 0.1175);
						}
						else{
							frm.set_value("gosi", (d.basic_salary + d.housing_allowance) * 0.02);
						}
						frm.set_value("end_of_services", (((frm.doc.basic + frm.doc.housing + frm.doc.transport) / 2 ) / 12));
						frm.set_value("oh_cost_total", frm.doc.gosi + frm.doc.end_of_services);
					}
				}
			});
		}
	},
	basic: function(frm){
		calc_total_salary(frm);
		calc_gosi(frm);
		calc_eos(frm);
		calc_oh_cost_total(frm);
	},
	housing: function(frm){
		calc_total_salary(frm);
		calc_gosi(frm);
		calc_eos(frm);
		calc_oh_cost_total(frm);
	},
	transport: function(frm){
		calc_total_salary(frm);
		calc_eos(frm);
		calc_oh_cost_total(frm);
	},
	mobile: function(frm){
		calc_total_salary(frm);
	},
	vt_allowance: function(frm){
		calc_total_salary(frm);
	},
	neom_allowance: function(frm){
		calc_total_salary(frm);
	},
	gasoline: function(frm){
		calc_total_salary(frm);
	},
	food: function(frm){
		calc_total_salary(frm);
	},
	transfer_fee: function(frm){
		frm.set_value("monthly_transfer_fee", frm.doc.transfer_fee / 12 );
		calc_oh_cost_total(frm);
	},
	transaction_fee: function(frm){
		calc_oh_cost_total(frm);
	},
	iqama_fee: function(frm){
		frm.set_value("monthly_iqama_fee", frm.doc.iqama_fee / 12 );
		calc_oh_cost_total(frm);
	},
	wl_fee: function(frm){
		frm.set_value("monthly_wl_fee", frm.doc.wl_fee / 12 );
		calc_oh_cost_total(frm);
	},
	leave_per_year_in_days: function(frm){
		let leave_amt_per_month = (((((frm.doc.basic || 0) + (frm.doc.housing || 0) + (frm.doc.transport || 0)) / 30 ) * frm.doc.leave_per_year_in_days ) / 12);
		frm.set_value("leave_amt_per_month", leave_amt_per_month);
		calc_oh_cost_total(frm);
	},
	exit_re_entry: function(frm){
		calc_Monthly_exitRE_TicktAmt(frm);
		calc_oh_cost_total(frm);
	},
	ticket_amount: function(frm){
		calc_Monthly_exitRE_TicktAmt(frm);
		calc_oh_cost_total(frm);
	},
	vacation_entitlement: function(frm){
		calc_Monthly_exitRE_TicktAmt(frm);
		calc_oh_cost_total(frm);
	},
	relocation_allowance: function(frm){
		calc_oh_cost_total(frm);
	},
	insurance_class: function(frm){
		if(frm.doc.insurance_class){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Insurance Category",
					name: frm.doc.insurance_class,
				},
				callback(r) {
					if(r.message) {
						var d = r.message;
						frm.set_value("yearly_med_inc", d.price);
						frm.set_value("monthly_med_inc", d.price / 12);
						calc_oh_cost_total(frm);
					}
				}
			});
		}
	},
	recruitment_cost: function(frm){
		calc_oh_cost_total(frm);
	},
	erc_fee: function(frm){
		calc_totals(frm);
	}
});

//function for calculating Monthly Exit Re-Entry(exitRE) and Ticket Amount Monthly
function calc_Monthly_exitRE_TicktAmt(frm){
	if(frm.doc.vacation_entitlement == "Yearly"){
		if(frm.doc.exit_re_entry){
			frm.set_value("exit_re_entry_monthly", frm.doc.exit_re_entry / 12 );
		}
		if(frm.doc.ticket_amount){
			frm.set_value("ticket_amount_monthly", frm.doc.ticket_amount / 12 );
		}
	}
	else if(frm.doc.vacation_entitlement == "Every Two Year"){
		if(frm.doc.exit_re_entry){
			frm.set_value("exit_re_entry_monthly", frm.doc.exit_re_entry / 24 );
		}
		if(frm.doc.ticket_amount){
			frm.set_value("ticket_amount_monthly", frm.doc.ticket_amount / 24 );
		}
	}
}

//function for calculationg total salary of employee
function calc_total_salary(frm){
	let total_salary = 0;

	total_salary += frm.doc.basic ?? 0;
	total_salary += frm.doc.housing ?? 0;
	total_salary += frm.doc.transport ?? 0;
	total_salary += frm.doc.mobile ?? 0;
	total_salary += frm.doc.vt_allowance ?? 0;
	total_salary += frm.doc.neom_allowance ?? 0;
	total_salary += frm.doc.gasoline ?? 0;
	total_salary += frm.doc.food ?? 0;

	frm.set_value("total_salary", total_salary);
	calc_totals(frm);
}

//calculating gosi and end of services on the basis of basic and housing 
function calc_gosi(frm){
	if(frm.doc.nationality == "Saudi Arabia"){
		let gosi = (((frm.doc.basic || 0) + (frm.doc.housing || 0)) * 0.1175);
		frm.set_value("gosi", gosi);
	}
	else{
		let gosi = (((frm.doc.basic || 0) + (frm.doc.housing || 0)) * 0.02);
		frm.set_value("gosi", gosi);
	}
}

//calculating end of service of employee
function calc_eos(frm){
	let eos_amt = ((((frm.doc.basic || 0) + (frm.doc.housing || 0) + (frm.doc.transport || 0)) / 2 ) / 12);
	frm.set_value("end_of_services", eos_amt);
}

//calculating total OH Cost on all expenses, fees, benefits of employee
function calc_oh_cost_total(frm){
	let total_oh_cost = 0;

    total_oh_cost += frm.doc.gosi ?? 0;
    total_oh_cost += frm.doc.transaction_fee ?? 0;
    total_oh_cost += frm.doc.monthly_transfer_fee ?? 0;
    total_oh_cost += frm.doc.monthly_iqama_fee ?? 0;
    total_oh_cost += frm.doc.monthly_wl_fee ?? 0;

    total_oh_cost += frm.doc.leave_amt_per_month ?? 0;
    total_oh_cost += frm.doc.exit_re_entry_monthly ?? 0;
    total_oh_cost += frm.doc.ticket_amount_monthly ?? 0;
    total_oh_cost += frm.doc.end_of_services ?? 0;
	total_oh_cost += frm.doc.relocation_allowance ?? 0;

    total_oh_cost += frm.doc.monthly_med_inc ?? 0;
	total_oh_cost += frm.doc.recruitment_cost ?? 0;

    frm.set_value("oh_cost_total", total_oh_cost);
	calc_totals(frm);
    //console.log(total_oh_cost);
    frm.refresh();
}

//calculating totals
function calc_totals(frm){
	let total_with_erc = 0;
	total_with_erc += frm.doc.oh_cost_total ?? 0;
	total_with_erc += frm.doc.erc_fee ?? 0;

	frm.set_value("total_with_erc", total_with_erc);

	let total_cost = 0;
	total_cost += frm.doc.total_salary ?? 0;
	total_cost += frm.doc.total_with_erc ?? 0;
	
	frm.set_value("total_cost", total_cost);
}