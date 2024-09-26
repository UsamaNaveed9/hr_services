<h3>{{_("Job Requisition")}}</h3>

<p>{{ _("Your submitted Job Requisition: ") }} {{ doc.name }} {{ _("of Project: ") }} {{ doc.requested_by_name }} {{ _("has been approved") }}</p>

{% set doc_link = frappe.utils.get_url_to_form('Job Requisition', doc.name) %} 

<a href="{{ doc_link }}">Click Here</a>

<p>Thank you, good day!</p>