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
        callback: function(response) {
            if (response.message) {
                render_customer_list(page, response.message);
            }
        }
    });
}

function render_customer_list(page, customers) {
	// Clear existing content before rendering the updated customer list
	page.body.html('');

    var content = page.body.append('');
    var total = 0;
    for (var i = 0; i < customers.length; i++) {
        var customer = customers[i];
		var button = $('<button class="btn btn-default" style="width: 20%;font-size: large;font-weight: bold;margin-bottom: 5px;background-color: #3498db;color: #ffffff;padding: 5px 1px 5px 1px;"></button>').text(customer.project_name);
		var outstandingAmount = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(customer.outstanding_amount));
        total = total + customer.outstanding_amount;
        (function(customer) {
            button.on('click', function() {
                open_ar_report(customer.name);
            });
        })(customer);
        content.append(button);
		content.append(outstandingAmount);
        content.append('<br>');  // Add line break for better spacing
    }
    var t = $('<button class="btn btn-default" style="width: 20%;font-size: large;font-weight: bold;margin-bottom: 5px;color: black;padding: 5px 1px 5px 1px;"></button>').text("Total");
	var t_v = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(total));
    //content.append('<br>');
    content.append('<hr style="margin-right: 882px;border-top: 4px solid;width: 32%;">');
    content.append(t);
	content.append(t_v);
}

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

function refresh_customer_list(page){
	frappe.call({
        method: 'hr_services.hr_services.page.tracker.tracker.get_outstanding_customers',
        callback: function(response) {
            if (response.message) {
                render_customer_list(page, response.message);
            }
        }
    });
}