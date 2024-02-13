<h3>{{_("Request For Payment")}}</h3>

<p>{{ _("Please Take Action on Request For Payment: ") }} {{ doc.name }}</p>

{% set doc_link = frappe.utils.get_url_to_form('Request For Payment', doc.name) %} 

<a href="{{ doc_link }}">Click Here</a> 

<p>Thank you, good day!</p>
