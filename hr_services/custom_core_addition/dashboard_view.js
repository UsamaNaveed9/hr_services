
//when a dashboard loaded this dashboard_view.js file run
//file path: apps/frappe/frappe/core/page/dashboard_view/dashboard_view.js
//funciton: set_drop_down() exists under Dashboard class
//some additional lines written in the set_drop_down() function

class Dashboard {
    set_dropdown() {
        // this.page.clear_menu();
    
        // this.page.add_menu_item(__("Edit"), () => {
        //     frappe.set_route("Form", "Dashboard", frappe.dashboard.dashboard_name);
        // });
    
        // this.page.add_menu_item(__("New"), () => {
        //     frappe.new_doc("Dashboard");
        // });
    
        // this.page.add_menu_item(__("Refresh All"), () => {
        //     this.chart_group && this.chart_group.widgets_list.forEach((chart) => chart.refresh());
        //     this.number_card_group &&
        //         this.number_card_group.widgets_list.forEach((card) => card.render_card());
        // });

        // above commented lines are same
        if(frappe.dashboard.dashboard_name != "Master Dashboard"){ // this condition added to reduce the options
            frappe.db.get_list("Dashboard").then((dashboards) => {
                dashboards.map((dashboard) => {
                    let name = dashboard.name;
                    if (name != this.dashboard_name) {
                        this.page.add_menu_item(
                            name,
                            () => frappe.set_route("dashboard-view", name),
                            1
                        );
                    }
                });
            });
        }
    
        //below code addition added for adding the buttons in the Dashboard
        if(frappe.dashboard.dashboard_name == "Master Dashboard"){
            // Add a button with a label to the page
            let tracker_button = this.page.add_button(__('TRACKER - SUMMARY OF RECEIVABLES'), () => {
                frappe.set_route("tracker");
            });
        
            tracker_button.addClass('btn-primary');
    
            let profit_button = this.page.add_button(__('Monthly Income Statement'), () => {
                frappe.set_route("query-report","ERC Monthly Income Statement")
            })
    
            profit_button.addClass('btn-primary');
        }
    }
}
