// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('PO Management', {
	setup(frm) {
		frm.set_query("employee_no", function(){
		    return {
		        filters: [
		            ["Employee","project","in", "PROJ-0001"]
		        ]
		    }
		});
	},
	po_units(frm) {
		if(frm.doc.po_amount && frm.doc.po_units){
			calculate(frm);
		}
		if(frm.doc.used_units){
			frm.set_value("remaining_units", frm.doc.po_units - frm.doc.used_units );
		}
		else{
			frm.set_value("remaining_units", frm.doc.po_units );
		}
	},
	used_units(frm) {
		if(frm.doc.po_units){
			frm.set_value("remaining_units", frm.doc.po_units - frm.doc.used_units );
		}
	},
	po_amount(frm) {
		if(frm.doc.po_amount && frm.doc.po_units){
			calculate(frm);
		}
	}
});

function calculate(frm){
	let inv_rate = 0;
	let amount_wm = 0;
	let margin = 0;
	inv_rate = frm.doc.po_amount / frm.doc.po_units;
	amount_wm = frm.doc.po_amount / 1.08;
	margin = amount_wm * 0.08;
	frm.set_value("invoicing_rate",inv_rate);
	frm.set_value("margin",margin);
	frm.set_value("po_amount_wm",amount_wm);
};
