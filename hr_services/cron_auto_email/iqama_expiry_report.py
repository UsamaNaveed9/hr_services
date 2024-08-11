#CRON Job on 06:00 AM on 20th of each month will run
#send_email function will call

import calendar
from datetime import timedelta

import frappe
from frappe import _
from frappe.desk.query_report import build_xlsx_data
from frappe.model.document import Document
from frappe.utils import (
	add_to_date,
	cint,
	format_time,
	get_link_to_form,
	get_url_to_report,
	global_date_format,
	now,
	now_datetime,
	today,
	validate_email_address,
)
from frappe.utils.csvutils import to_csv
from frappe.utils.xlsxutils import make_xlsx
import datetime

class BuildReport:
	def __init__(self):
		#Report need that have to generate and send
		self.report = "Iqama Expiry and Cost"
		self.report_type = "Script Report"

		#There is a limit for no of rows
		self.no_of_rows = 500

		#User that have the permissions of report
		self.user = "Administrator"

		#Users that have role 'OPE EXP Approver'
		self.role = "OPE EXP Approver"

		#Recipients email that users have above Role
		self.email_to = get_recipients(self)
		
		#Report Format 
		self.format = "HTML"

		# Get the current date
		now = datetime.datetime.now()

		# Calculate the first day of the next month
		if now.month == 12:  # December
			next_month_date = datetime.datetime(now.year + 1, 1, 1)
		else:
			next_month_date = datetime.datetime(now.year, now.month + 1, 1)

		# Get the next month as a string (e.g., "Jan", "Feb", etc.)
		next_month = next_month_date.strftime("%b")

		# Get the current or next year depending on the month
		next_year = next_month_date.year

		# Set the dynamic values in the filters dictionary
		self.filters = {
			"fiscal_year": str(next_year),
			"month": next_month,
			"company": "Elite Resources Center"
		}

	def get_html_table(self, columns=None, data=None):

		date_time = global_date_format(now()) + " " + format_time(now())
		report_doctype = frappe.db.get_value("Report", self.report, "ref_doctype")

		return frappe.render_template(
			"frappe/templates/emails/auto_email_report.html",
			{
				"title": "Employees List that Iqama going to Expiry",
				"description": "Renew the Iqama of these Employees",
				"date_time": date_time,
				"columns": columns,
				"data": data,
				"report_url": get_url_to_report(self.report, self.report_type, report_doctype),
				"report_name": self.report,
			},
		)	

@frappe.whitelist()
def get_report_content(self):
	"""Returns file in for the report in given format"""
	report = frappe.get_doc("Report", self.report)
	
	self.filters = frappe.parse_json(self.filters) if self.filters else {}

	columns, data = report.get_data(
		limit=self.no_of_rows or 100,
		user=self.user,
		filters=self.filters,
		as_dict=True,
		ignore_prepared_report=True,
		are_default_filters=False,
	)

	# add serial numbers
	columns.insert(0, frappe._dict(fieldname="idx", label="", width="30px"))
	for i in range(len(data)):
		data[i]["idx"] = i + 1

	if len(data) == 0:
		return None
	
	if self.format == "HTML":
		columns, data = make_links(columns, data)
		columns = update_field_types(columns)
		return self.get_html_table(columns, data)

	elif self.format == "XLSX":
		report_data = frappe._dict()
		report_data["columns"] = columns
		report_data["result"] = data

		xlsx_data, column_widths = build_xlsx_data(report_data, [], 1, ignore_visible_idx=True)
		xlsx_file = make_xlsx(xlsx_data, "Auto Email Report", column_widths=column_widths)
		return xlsx_file.getvalue()
	else:
		frappe.throw(_("Invalid Output Format"))        	


@frappe.whitelist()			
def send_email():
		self = BuildReport()

		data = get_report_content(self)

		if not data:
			return

		attachments = None
		if self.format == "HTML":
			message = data
		else:
			message = self.get_html_table()

		if not self.format == "HTML":
			attachments = [{"fname": self.get_file_name(), "fcontent": data}]

		for recipient_email in self.email_to:
			frappe.sendmail(
				recipients=recipient_email,
				subject="Employee List those iqama will Expiry Next Month",
				message=message,
				attachments=attachments,
			)            
		
def make_links(columns, data):
	for row in data:
		doc_name = row.get("name")
		for col in columns:
			if not row.get(col.fieldname):
				continue

			if col.fieldtype == "Link":
				if col.options and col.options != "Currency":
					row[col.fieldname] = get_link_to_form(col.options, row[col.fieldname])
			elif col.fieldtype == "Dynamic Link":
				if col.options and row.get(col.options):
					row[col.fieldname] = get_link_to_form(row[col.options], row[col.fieldname])
			elif col.fieldtype == "Currency":
				doc = frappe.get_doc(col.parent, doc_name) if doc_name and col.get("parent") else None
				# Pass the Document to get the currency based on docfield option
				row[col.fieldname] = frappe.format_value(row[col.fieldname], col, doc=doc)
	return columns, data

def update_field_types(columns):
	for col in columns:
		if col.fieldtype in ("Link", "Dynamic Link", "Currency") and col.options != "Currency":
			col.fieldtype = "Data"
			col.options = ""
	return columns

def get_html_table(self, columns=None, data=None):

		date_time = global_date_format(now()) + " " + format_time(now())
		report_doctype = frappe.db.get_value("Report", self.report, "ref_doctype")

		return frappe.render_template(
			"frappe/templates/emails/auto_email_report.html",
			{
				"title": self.name,
				"description": self.description,
				"date_time": date_time,
				"columns": columns,
				"data": data,
				"report_url": get_url_to_report(self.report, self.report_type, report_doctype),
				"report_name": self.report,
				"edit_report_settings": get_link_to_form("Auto Email Report", self.name),
			},
		)

def get_recipients(self):
	# Query to get user IDs of users with the specified role
	user_roles = frappe.get_all('Has Role', filters={'role': self.role, 'parenttype': 'User'}, fields=['parent'])

	# Extract the user IDs from the query result except Administrator and Guest User
	user_ids = [user['parent'] for user in user_roles if user['parent'] not in ['Administrator', 'Guest']]

	# Fetch the user details based on the filtered user IDs
	users = frappe.get_all('User', filters={'name': ['in', user_ids]}, fields=['name', 'full_name', 'email'])

	# Filter out users with empty email fields and concatenate emails
	email_list = [user['email'] for user in users if user['email']]
	
	return email_list