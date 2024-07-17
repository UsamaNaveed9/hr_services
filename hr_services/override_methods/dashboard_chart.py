
import frappe
from frappe import _
from frappe.desk.doctype.dashboard_chart.dashboard_chart import (
	DashboardChart,
	get_group_by_chart_config,
	get_heatmap_chart_config,
	get_chart_config
)

from frappe.utils import get_datetime
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
	refresh=None,
):
	if chart_name:
		chart: DashboardChart = frappe.get_doc("Dashboard Chart", chart_name)
	else:
		chart = frappe._dict(frappe.parse_json(chart))

	heatmap_year = heatmap_year or chart.heatmap_year
	timespan = timespan or chart.timespan

	if timespan == "Select Date Range":
		if from_date and len(from_date):
			from_date = get_datetime(from_date)
		else:
			from_date = chart.from_date

		if to_date and len(to_date):
			to_date = get_datetime(to_date)
		else:
			to_date = get_datetime(chart.to_date)

	timegrain = time_interval or chart.time_interval
	filters = frappe.parse_json(filters) or frappe.parse_json(chart.filters_json)
	if not filters:
		filters = []

	# don't include cancelled documents
	filters.append([chart.document_type, "docstatus", "<", 2, False])

	if chart.chart_type == "Group By":
		chart_config = get_group_by_chart_config(chart, filters)
	else:
		if chart.type == "Heatmap":
			chart_config = get_heatmap_chart_config(chart, filters, heatmap_year)
		else:
			chart_config = get_chart_config(chart, filters, timespan, timegrain, from_date, to_date)
	
	if chart.group_by_based_on == "requested_by" or chart.group_by_based_on == "project":
		new_labels = []
		labels = chart_config["labels"]
		for lb in labels:
			project_name = frappe.db.get_value("Project", lb, "project_name")
			new_labels.append(f"{lb} ({project_name})")
		
		chart_config["labels"] = new_labels
	
	return chart_config