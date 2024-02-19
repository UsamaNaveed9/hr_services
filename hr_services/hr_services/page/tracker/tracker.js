frappe.pages['tracker'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'TRACKER - SUMMARY OF RECEIVABLES',
		single_column: true
	});

	var refresh_button = page.add_inner_button('Refresh', function() {
        // Reload the data when the refresh button is clicked
        refresh_customer_list(page);
    });

	frappe.call({
        method: 'hr_services.hr_services.page.tracker.tracker.get_outstanding_customers',
        callback: function(r) {
            if (r.message) {
                //r.message[0] contain all customers array, r.message[1][0].total_advance_outstanding contain outstanding amount of clients, r.message[2][0].total_advance_outstanding contain the outstanding amount of Elite HQ
                render_customer_list(page, r.message[0], r.message[1][0].total_advance_outstanding, r.message[2][0].total_advance_outstanding);
            }
        }
    });
}

function render_customer_list(page, customers, client_outstanding_adv, elite_outstanding_adv) {
	// Clear existing content before rendering the updated customer list
	page.body.html('');

    var content = page.body.append('');
    var total = 0;
    for (var i = 0; i < customers.length; i++) {
        var customer = customers[i];

        if (i === 0) {
            total = total + customer.outstanding_amount;
            row = two_button_row(customer,client_outstanding_adv)
            content.append(row);
        }
        else if (i === 1) {    
                total = total + customer.outstanding_amount;
                row = two_button_row(customer,elite_outstanding_adv)
                content.append(row);
        }     
        else {
            // For other values of i, create buttons and amounts without the second button
            var button = $('<button class="btn btn-default" style="width: 20%; font-size: large; font-weight: bold; margin-bottom: 5px; padding: 5px 1px 5px 1px;"></button>').text(customer.project_name);
        
            var outstandingAmount = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(customer.outstanding_amount));
            
            total = total + customer.outstanding_amount;

            (function (customer) {
                button.on('click', function () {
                    open_ar_report(customer.name);
                });
            })(customer);
        
            content.append(button);
            content.append(outstandingAmount);
        }
        
        content.append('<br>'); // Add line break for better spacing
    }
    var total_button = $('<button class="btn btn-default" style="width: 20%;font-size: large;font-weight: bold;margin-bottom: 5px;padding: 5px 1px 5px 1px;"></button>').text("Total");
	var total_value = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(total));
    //content.append('<br>');
    content.append('<hr style="margin-right: 882px;border-top: 4px solid;width: 32%;">');
    content.append(total_button);
	content.append(total_value);
}
//this function make url for Invoice Details report
function open_ar_report(customer_name) {
    var filters = {
        "company": "Elite Resources Center",
        "customer": customer_name,
        "status": "Unpaid"
    };

    var query_string = $.param(filters);
    var url = "/app/query-report/Invoices Detail?" + query_string;
     // Open the report in a new tab
     window.open(url, '_blank');
}
//on click refresh button
function refresh_customer_list(page){
	frappe.call({
        method: 'hr_services.hr_services.page.tracker.tracker.get_outstanding_customers',
        callback: function(r) {
            if (r.message) {
                //r.message[0] contain all customers array, r.message[1][0].total_advance_outstanding contain outstanding amount of clients, r.message[2][0].total_advance_outstanding contain the outstanding amount of Elite HQ
                render_customer_list(page, r.message[0], r.message[1][0].total_advance_outstanding,r.message[2][0].total_advance_outstanding);
            }
        }
    });
}
//this function make url for ERC Loan Report
function open_loan_report() {
    var filters = {
        "company": "Elite Resources Center",
        "applicant_type": "Employee"
    };

    var query_string = $.param(filters);
    var url = "/app/query-report/ERC Loan Report?" + query_string;
     // Open the report in a new tab
     window.open(url, '_blank');
}

function two_button_row(customer,outstanding_adv){
    // Create a new row only when i is 0
    var row = $('<div style="display: flex; align-items: center; margin-bottom: -20px;"></div>');
        
    var button = $('<button class="btn btn-default" style="width: 20%; font-size: large; font-weight: bold; margin-bottom: 5px; padding: 5px 1px 5px 1px;"></button>').text(customer.project_name);

    var outstandingAmount = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(customer.outstanding_amount));

    (function (customer) {
        button.on('click', function () {
            open_ar_report(customer.name);
        });
    })(customer);

    var spaceBetweenButtons = $('<div style="width: 200px;"></div>'); // Adjust the width for desired spacing

    var AdvanceButton = $('<button class="btn btn-default" style="width: 20%; font-size: large; font-weight: bold; margin-left: 10px; margin-bottom: 5px; padding: 5px 1px 5px 1px;"></button>').text('Emp Advances (Elite HQ)');

    var RemainingAmount = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(outstanding_adv));
    
    (function () {
        AdvanceButton.on('click', function () {
            open_loan_report();
        });
    })();

    row.append(button);
    row.append(outstandingAmount);
    row.append(spaceBetweenButtons);
    row.append(AdvanceButton);
    row.append(RemainingAmount);

    return row;
}