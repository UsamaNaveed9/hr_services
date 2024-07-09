

//add new codition in 'else if' of add_context_buttons event
//below is the new code after added the condition in 'else if'

frappe.ui.form.on('Payroll Entry', {
    add_context_buttons: function (frm) {
        if (frm.doc.salary_slips_submitted || (frm.doc.__onload && frm.doc.__onload.submitted_ss)) {
            frm.events.add_bank_entry_button(frm);
        } else if (frm.doc.salary_slips_created && frm.doc.status !== "Queued" && frm.doc.custom_approved) {
            frm.add_custom_button(__("Submit Salary Slip"), function() {
                submit_salary_slip(frm);
            }).addClass("btn-primary");
        } else if (!frm.doc.salary_slips_created && frm.doc.status === "Failed") {
            frm.add_custom_button(__("Create Salary Slips"), function() {
                frm.trigger("create_salary_slips");
            }).addClass("btn-primary");
        }
    }
});