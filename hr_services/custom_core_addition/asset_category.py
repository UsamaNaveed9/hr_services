

import frappe
from frappe import _
from frappe.model.document import Document

#this update in the core code file
#Updated lines are mentioned with '#this'

class AssetCategory(Document):
	def validate(self):
		self.validate_finance_books()
		if self.custom_is_for_amortization == 0:        #this
			self.validate_account_types()               #this
		self.validate_account_currency()
		self.valide_cwip_account()