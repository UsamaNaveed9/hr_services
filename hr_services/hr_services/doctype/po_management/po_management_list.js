
frappe.listview_settings['PO Management'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Draft": "grey",
			"Active": "blue",
			"Completed": "green"
		};
		return [__(doc.status), status_colors[doc.status], "status,=,"+doc.status];
	}
};