// Copyright (c) 2023, Elite Resources and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Category', {
	onload: function(frm) {
        if(frm.doc.custom_is_for_amortization == 1){
            frm.set_query('fixed_asset_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "root_type": "Asset",
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });
    
            frm.set_query('accumulated_depreciation_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });   
        }
    },
    custom_is_for_amortization: function(frm){
        if(frm.doc.custom_is_for_amortization == 1){
            frm.clear_table("accounts");
            frm.refresh_fields();
            frm.set_query('fixed_asset_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "root_type": "Asset",
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });
    
            frm.set_query('accumulated_depreciation_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });   
        }
        else{
            frm.clear_table("accounts");
            frm.refresh_fields();
            frm.set_query('fixed_asset_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "account_type": "Fixed Asset",
                        "root_type": "Asset",
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });
    
            frm.set_query('accumulated_depreciation_account', 'accounts', function(doc, cdt, cdn) {
                var d  = locals[cdt][cdn];
                return {
                    "filters": {
                        "account_type": "Accumulated Depreciation",
                        "is_group": 0,
                        "company": d.company_name
                    }
                };
            });
        }
    }
})