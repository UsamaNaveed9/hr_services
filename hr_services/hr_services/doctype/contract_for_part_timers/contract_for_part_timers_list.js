
frappe.listview_settings['Contract For Part Timers'] = {
    get_indicator: function(doc) {
		var colors = {
			"Inactive": "grey",
			"Active": "green",
			"Unsigned": "red"
		};
		return [__(doc.status), colors[doc.status], "status,=,"+doc.status];
	}
};