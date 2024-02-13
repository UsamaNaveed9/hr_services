<h3>{{_("Purchase Invoice")}}</h3>

<p>{{ _("Please Take an Action on Purchase Invoice: ") }} {{ doc.name }}</p>

{% set doc_link = frappe.utils.get_url_to_form('Purchase Invoice', doc.name) %} 

<a href="{{ doc_link }}">Click Here</a> 

<p>Thank you, good day!</p>
