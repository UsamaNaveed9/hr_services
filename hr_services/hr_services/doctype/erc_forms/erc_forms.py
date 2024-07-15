# Copyright (c) 2024, Elite Resources and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days
from frappe.model.document import Document

class ERCForms(Document):
	def before_insert(self):
		if self.employee:
			updates = {}
			updates["custom_probation_period"] = 180
			updates["custom_probation_end_date"] = add_days(self.employment_date, 180 - 1)
			frappe.db.set_value("Employee", self.employee, updates, update_modified=False)
			frappe.db.commit()

			
# import frappe
# from frappe import _
# import re
# from frappe.model.document import Document
# from frappe.core.api.file import create_new_folder
# from frappe.model.naming import _format_autoname
# from frappe.realtime import publish_realtime
# from frappe.utils.weasyprint import PrintFormatGenerator

# class ERCForms(Document):
# 	def validate(self):
# 		#frappe.errprint(self.workflow_state)
# 		if self.workflow_state == "Approved":

# 			print_format = "ERC Form"
# 			letter_head = "letterhead"

# 			fallback_language = "en"

# 			args = {
# 				"doctype": self.doctype,
# 				"name": self.name,
# 				"title": self.employee_name,
# 				"lang": getattr(self, "language", fallback_language),
# 				"show_progress": 1,
# 				"print_format": print_format,
# 				"letter_head": letter_head,
# 			}

# 			frappe.enqueue(
# 				method=self.execute,
# 				timeout=30,
# 				now=bool(
# 					1
# 					or frappe.flags.in_test
# 					or frappe.conf.developer_mode
# 				),
# 				**args,
# 			)


# 	def execute(
# 		doctype,
# 		name,
# 		title=None,
# 		lang=None,
# 		show_progress=True,
# 		print_format=None,
# 		letter_head=None,
# 	):
# 		"""
# 		Queue calls this method, when it's ready.

# 		1. Create necessary folders
# 		2. Get raw PDF data
# 		3. Save PDF file and attach it to the document
# 		"""

# 		def publish_progress(percent):
# 			publish_realtime(
# 				"progress",
# 				{"percent": percent, "title": _("Creating PDF ..."), "description": None},
# 				doctype=doctype,
# 				docname=name,
# 			)

# 		if lang:
# 			frappe.local.lang = lang
# 			# unset lang and jenv to load new language
# 			frappe.local.lang_full_dict = None
# 			frappe.local.jenv = None

# 		if show_progress:
# 			publish_progress(0)

# 		if show_progress:
# 			publish_progress(33)

# 		if frappe.db.get_value("Print Format", print_format, "print_format_builder_beta"):
# 			doc = frappe.get_doc(doctype, name)
# 			pdf_data = PrintFormatGenerator(print_format, doc, letter_head).render_pdf()
# 		else:
# 			pdf_data = get_pdf_data(doctype, name, print_format, letter_head)

# 		if show_progress:
# 			publish_progress(66)

# 		save_and_attach(pdf_data, name, title)

# 		if show_progress:
# 			publish_progress(100)


# def get_pdf_data(doctype, name, print_format: None, letterhead: None):
# 	"""Document -> HTML -> PDF."""
# 	html = frappe.get_print(doctype, name, print_format, letterhead=letterhead)
# 	frappe.errprint(html)
# 	custom_css = """
# 	<style>
# 	p.oblique {
# 	  font-style: oblique;
# 	}
# 	#fd {
# 		display: inline;
# 	  margin-left:550px;
# 	}
# 	#ffd {
# 		display: inline;
# 	  margin-left:0px;
# 	}
# 	#ppd {
# 		display: inline;
# 	  /*background-color: lightgrey;*/
# 	  width: 260px;
# 	  margin-left:0px;
# 	  height: 35px;
# 	  /*border: 1px solid black;*/
# 	}
# 	.table-bordered, td{
# 		border-color: #000000!important;
# 	}
# 	.sign-div {
# 	width: 100%;
# 	margin-top: 0px;
# 	}
# 	.print-format .sign-div.col-xs-12 img {
# 		width: 16% !important;
# 		padding-top: 5px;
# 		padding-left: 5px;
# 	}
# 	.sign-div .col-xs-12 {
# 		padding-left: 0px;
# 		padding-right: 0px;
# 	}
# 	.sign-div2 {
# 	width: 100%;
# 	margin-top: 0px;
# 	}
# 	.print-format .sign-div2.col-xs-12 img {
# 		width: 45% !important;
# 		padding-top: 0px;
# 		padding-left: 0px;
# 	}
# 	.sign-div2 .col-xs-12 {
# 		padding-left: 0px;
# 		padding-right: 0px;
# 	}
# 	.sign-div3 {
# 	width: 100%;
# 	margin-top: 0px;
# 	}
# 	.print-format .sign-div3.col-xs-12 img {
# 		width: 30% !important;
# 		padding-top: 0px;
# 		padding-left: 0px;
# 	}
# 	.sign-div3 .col-xs-12 {
# 		padding-left: 0px;
# 		padding-right: 0px;
# 	}
# 	.arabicembassytable{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:15px;
# 		text-align:center;
# 	}
# 	.arabic{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:15px;
# 		text-align:right;
# 	}
# 	.arabicdiv{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:18px;
# 		text-align:right;
# 	}
# 	.arabicdiv-centr{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:18px;
# 		text-align:center;
# 	}
# 	.arabic_salary_table{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:15px;
# 	}
# 	.headingnote_arabic{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:18px;
# 	}
# 	.date_en{
# 		font-family: 'Arial', sans-serif;
# 		color: black;
# 		font-size:18px;
# 	}
# 	.footer {
# 		position: fixed;
# 		bottom: 0;
# 		padding-bottom: 0px;
# 		left: 0;
# 		right: 0;
# 	}
# 	@media print {
# 			.footer-img {

# 				bottom: 0;
# 			}
# 		}
# 	</style>
# 	"""

# 	# Remove existing <style> tags and their content
# 	cleaned_html = re.sub(r'<style[\s\S]*?</style>', '', html)

# 	#Inject the custom CSS at the beginning of the HTML
# 	html_with_custom_css = f"{custom_css}{cleaned_html}"
# 	frappe.errprint(html_with_custom_css)
# 	return frappe.utils.pdf.get_pdf(html_with_custom_css)


# def save_and_attach(content, to_name, title):
# 	"""
# 	Save content to disk and create a File document.

# 	File document is linked to another document.
# 	"""
	
# 	file_name = "{title}.pdf".format(title=title.replace(" ", "-"))

# 	file = frappe.new_doc("File")
# 	file.file_name = file_name
# 	file.content = content
# 	file.is_private = 0
# 	file.attached_to_doctype = "ERC Forms"
# 	file.attached_to_name = to_name
# 	file.save()
