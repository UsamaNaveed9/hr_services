

#Add loan_type arg in dict in the function of cord file
#Function Name: set_loan_repayment(self)
#Below is the New Funcation code

def set_loan_repayment(self):
		self.total_loan_repayment = 0
		self.total_interest_amount = 0
		self.total_principal_amount = 0
		
        # below all commented because calculate function not exist in this file

		# if not self.get("loans"):
		# 	for loan in self.get_loan_details():

		# 		amounts = calculate_amounts(loan.name, self.posting_date, "Regular Payment")

		# 		if amounts["interest_amount"] or amounts["payable_principal_amount"]:
		# 			self.append(
		# 				"loans",
		# 				{
		# 					"loan": loan.name,
		# 					"loan_type": loan.loan_type,
		# 					"total_payment": amounts["interest_amount"] + amounts["payable_principal_amount"],
		# 					"interest_amount": amounts["interest_amount"],
		# 					"principal_amount": amounts["payable_principal_amount"],
		# 					"loan_account": loan.loan_account,
		# 					"interest_income_account": loan.interest_income_account,
		# 				},
		# 			)