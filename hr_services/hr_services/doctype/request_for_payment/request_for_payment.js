// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request For Payment', {
	setup(frm) {
		frm.fields_dict['items'].grid.get_field("item").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item', 'item_group', 'in',frm.doc.expense_type],
				]
			}
        }

		frm.fields_dict['items'].grid.get_field("employee_no").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project],
				]
			}
        }

		frm.fields_dict['invoices'].grid.get_field("purchase_invoice").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Purchase Invoice', 'supplier', 'in',frm.doc.supplier],
					['Purchase Invoice', 'outstanding_amount', '>', 0 ],
					['Purchase Invoice', 'docstatus', '=', 1]
				]
			}
        }

		frm.fields_dict['employees'].grid.get_field("employee_no").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project],
					['Employee', 'employment_type', 'in','Part-time']
				]
			}
        }

		frm.fields_dict['advances'].grid.get_field("employee_no").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'project', 'in',frm.doc.project]
				]
			}
        }

		frm.fields_dict['employees'].grid.get_field("po_mgt").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			return {
				filters: [
					['PO Management', 'employee_no', '=',row.employee_no],
					['PO Management', 'status', 'in','Active']
				]
			}
        }
	},
	project(frm){
		//console.log(frm.doc.is_invoice_optional);
		if(frm.doc.is_invoice_optional == 1){
			frm.set_value("invoice_to_client","");
		}
		else if(frm.doc.is_invoice_optional == 0){
			frm.set_value("invoice_to_client","Yes");
		}
	},
	expense_type(frm){
		if(frm.doc.expense_type == 'Operational Expense' || frm.doc.expense_type == 'Recruitment Expense' || frm.doc.expense_type == 'Reimbursement Expense'){
			cur_frm.clear_table("items");
			frm.refresh_field("items");
			frm.set_value("project","");
			frm.set_value("total_amount",0);
		}
		if(frm.doc.expense_type == 'Supplier Payment'){
			cur_frm.clear_table("invoices");
			frm.refresh_field("invoices");
			frm.set_value("project","");
			frm.set_value("supplier","");
			frm.set_value("total_amount",0);
		}
		if(frm.doc.expense_type == 'Payment For Part Timer'){
			frm.set_value("project","PROJ-0001");
			cur_frm.clear_table("employees");
			frm.refresh_field("employees");
			frm.set_value("total_amount",0);
		}
		if(frm.doc.expense_type == 'Employee Advance'){
			frm.set_value("project","");
			cur_frm.clear_table("advances");
			frm.refresh_field("advances");
			frm.set_value("total_amount",0);
		}
	},
	before_save(frm){
		if(frm.doc.expense_type == 'Operational Expense' || frm.doc.expense_type == 'Recruitment Expense' || frm.doc.expense_type == 'Reimbursement Expense'){
			let total = 0;
			for(let i in frm.doc.items){
					total += frm.doc.items[i].amount;
				}
			frm.set_value("total_amount", total);
			frm.refresh();
		}
		if(frm.doc.expense_type == 'Supplier Payment'){
			let total = 0;
			for(let i in frm.doc.invoices){
				total += frm.doc.invoices[i].paid_amount;
			}
			frm.set_value("total_amount", total);
			frm.refresh();
		}
		if(frm.doc.expense_type == 'Payment For Part Timer'){
			let total = 0;
			for(let i in frm.doc.employees){
				total += frm.doc.employees[i].amount;
			}
			frm.set_value("total_amount", total);
			frm.refresh();
		}
		if(frm.doc.expense_type == 'Employee Advance'){
			let total = 0;
			for(let i in frm.doc.advances){
				total += frm.doc.advances[i].advance_amount;
			}
			frm.set_value("total_amount", total);
			frm.refresh();
		}
	}
});

frappe.ui.form.on("Request for Payment Details", {
	item:function(frm, cdt, cdn){
		let row = locals[cdt][cdn];
		if(row.item){
			frappe.db.get_value("Item Price", {"item_code":row.item, "selling":1}, "price_list_rate").then((r)=>{
				if(r.message.price_list_rate){
					let price = 0;
					price = r.message.price_list_rate;

					row.rate = price;
					if(!row.qty){
						row.qty = 1;
					}
					row.amount = row.qty * price;
					let total = 0;
					for(let i in frm.doc.items){
						total += frm.doc.items[i].amount;
					}
					frm.set_value("total_amount", total);
					frm.refresh();
				}
			})
		}
	},
	qty:function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	rate:function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	items_remove(frm,cdt,cdn){
		let total = 0;
		for(let i in frm.doc.items){
				total += frm.doc.items[i].amount;
			}
		frm.set_value("total_amount", total);
		frm.refresh();
	}
});

frappe.ui.form.on("RFP Supplier Details", {
	purchase_invoice:function(frm, cdt, cdn){
		let row = locals[cdt][cdn];
		if(row.purchase_invoice){
			frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Purchase Invoice",
                    name: row.purchase_invoice,
                },
                callback(r) {
                    if(r.message) {
                        var d = r.message;
						row.supplier = d.supplier
						row.grand_total = d.grand_total
						row.outstanding_amount = d.outstanding_amount
						row.project = d.project
						row.project_name = d.project_name

						let total = 0;
						for(let i in frm.doc.invoices){
							total += frm.doc.invoices[i].paid_amount;
						}
						frm.set_value("total_amount", total);
						frm.refresh();
                    }
                }
            });
		}
	},
	paid_amount:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.outstanding_amount && row.paid_amount > row.outstanding_amount){
			row.paid_amount = 0;
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Paid Amount cannot be greater than Outstanding amount')
			});
		}
		let total = 0;
		for(let i in frm.doc.invoices){
			total += frm.doc.invoices[i].paid_amount;
		}
		frm.set_value("total_amount", total);
		frm.refresh();
	},
	invoices_remove(frm,cdt,cdn){
		let total = 0;
		for(let i in frm.doc.invoices){
			total += frm.doc.invoices[i].paid_amount;
		}
		frm.set_value("total_amount", total);
		frm.refresh();
	}
});

frappe.ui.form.on("RFP Part Timer Details", {
	po_mgt:function(frm, cdt, cdn){
		let row = locals[cdt][cdn];
		if(row.po_mgt){
			frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "PO Management",
                    name: row.po_mgt
                },
                callback(r) {
                    if(r.message) {
                        var d = r.message;
						row.po_no = d.po_no;
						row.remaining_units = d.remaining_units;
						row.emp_rate = d.employee_rate;
						row.working_days = 0;
						row.amount = 0;

						let total = 0;
						for(let i in frm.doc.employees){
							total += frm.doc.employees[i].amount;
						}
						frm.set_value("total_amount", total);
						frm.refresh();
                    }
                }
            });
		}
	},
	working_days:function(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		if(row.emp_rate && row.working_days <= row.remaining_units){
			let amt = row.emp_rate * row.working_days;
			row.amount = amt
			
			let total = 0;
			for(let i in frm.doc.employees){
				total += frm.doc.employees[i].amount;
			}
			frm.set_value("total_amount", total);
			frm.refresh();
		}
		else if(row.working_days > row.remaining_units){
			row.working_days = 0;
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Working Days not greater than Remaining Units')
			});
		}
		else{
			row.working_days = 0;
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Please select PO first')
			});
		}
	},
	employees_remove(frm,cdt,cdn){
		let total = 0;
		for(let i in frm.doc.employees){
			total += frm.doc.employees[i].amount;
		}
		frm.set_value("total_amount", total);
		frm.refresh();
	}
});

frappe.ui.form.on("RFP Employee Advances", {
	monthly_repay_amount:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.advance_amount && row.monthly_repay_amount > row.advance_amount){
			row.monthly_repay_amount = 0;
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Monthly Repay Amount cannot be greater than Advance amount')
			});
		}
	},
	advance_amount:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.monthly_repay_amount && row.monthly_repay_amount > row.advance_amount){
			row.monthly_repay_amount = 0;
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Monthly Repay Amount cannot be greater than Advance amount')
			});
		}
		let total = 0;
		for(let i in frm.doc.advances){
			total += frm.doc.advances[i].advance_amount;
		}
		frm.set_value("total_amount", total);
		frm.refresh();
	},
	advances_remove(frm,cdt,cdn){
		let total = 0;
		for(let i in frm.doc.advances){
			total += frm.doc.advances[i].advance_amount;
		}
		frm.set_value("total_amount", total);
		frm.refresh();
	}
});

function calculate_amount(frm, cdt, cdn){
	let row = locals[cdt][cdn];
	row.amount = row.qty * row.rate;
	let total = 0;
	for(let i in frm.doc.items){
		total += frm.doc.items[i].amount;
	}
	frm.set_value("total_amount", total);
	frm.refresh();
}
