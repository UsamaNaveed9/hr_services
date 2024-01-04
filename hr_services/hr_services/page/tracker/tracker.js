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
    for (var i = 0; i < customers.length; i++) {
        var customer = customers[i];
		var button = $('<button class="btn btn-default" style="width: 25%;font-size: large;font-weight: bold;margin-bottom: 5px;background-color: #3498db;color: #ffffff;padding: 5px 1px 5px 1px;"></button>').text(customer.project_name);
		var outstandingAmount = $('<span style="margin-left: 30px; font-weight: bold;"></span>').text(format_currency(customer.outstanding_amount));
        button.on('click', function() {
            open_ar_report(customer.name);
        });
        content.append(button);
		content.append(outstandingAmount);
        content.append('<br>');  // Add line break for better spacing
        //content.append(`<div><a href="#" onclick="open_ar_report('${customer.name}')">${customer.customer_name}</a> - ${customer.outstanding_amount}</div>`);
    }
}

function open_ar_report(customer_name) {
    frappe.ui.open_route('query-report', 'Accounts Receivable', {
        'customer': customer_name
    });
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