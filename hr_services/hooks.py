from . import __version__ as app_version

app_name = "hr_services"
app_title = "HR Services"
app_publisher = "Elite Resources"
app_description = "HR Additional Services"
app_email = "usamanaveed9263@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hr_services/css/hr_services.css"
# app_include_js = "/assets/hr_services/js/hr_services.js"

# include js, css files in header of web template
# web_include_css = "/assets/hr_services/css/hr_services.css"
# web_include_js = "/assets/hr_services/js/hr_services.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hr_services/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Employee" : "customjs/employee.js",
              "Sales Invoice": "customjs/sales_invoice.js",
              "Project": "customjs/project.js",
              "Payroll Entry": "customjs/payroll_entry.js",
              "Purchase Invoice": "customjs/purchase_invoice.js"
              }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "hr_services.utils.jinja_methods",
#	"filters": "hr_services.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hr_services.install.before_install"
# after_install = "hr_services.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hr_services.uninstall.before_uninstall"
# after_uninstall = "hr_services.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hr_services.utils.before_app_install"
# after_app_install = "hr_services.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hr_services.utils.before_app_uninstall"
# after_app_uninstall = "hr_services.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hr_services.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Employee": {
        "on_update": "hr_services.custompy.employee.update_salary"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"hr_services.tasks.all"
#	],
#	"daily": [
#		"hr_services.tasks.daily"
#	],
#	"hourly": [
#		"hr_services.tasks.hourly"
#	],
#	"weekly": [
#		"hr_services.tasks.weekly"
#	],
#	"monthly": [
#		"hr_services.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "hr_services.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "hr_services.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "hr_services.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hr_services.utils.before_request"]
# after_request = ["hr_services.utils.after_request"]

# Job Events
# ----------
# before_job = ["hr_services.utils.before_job"]
# after_job = ["hr_services.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"hr_services.auth.validate"
# ]
