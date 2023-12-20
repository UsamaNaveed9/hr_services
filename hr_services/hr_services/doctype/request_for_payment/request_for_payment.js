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
							total += frm.doc.invoices[i].outstanding_amount;
						}
						frm.set_value("total_amount", total);
						frm.refresh();
                    }
                }
            });
		}
	},
	invoices_remove(frm,cdt,cdn){
		let total = 0;
		for(let i in frm.doc.invoices){
			total += frm.doc.invoices[i].outstanding_amount;
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
