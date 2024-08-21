// Copyright (c) 2024, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Received No Breakdown', {
	before_save(frm){
		calculate_total(frm);
	}
});

frappe.ui.form.on("Payment Received Items", {
	amount(frm){
		calculate_total(frm);
	},
	receiving_details_remove(frm){
		calculate_total(frm);
	}
});

function calculate_total(frm){
	let total = 0;
	for(let i in frm.doc.receiving_details){
		total += frm.doc.receiving_details[i].amount;
	}
	frm.set_value("total_received_amount", total);
	frm.refresh();
}
