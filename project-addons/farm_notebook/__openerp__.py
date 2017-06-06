# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Farm notebook",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        'res_partner_farm_data',
        'product',
        'account',
        'account_analytic_plans'
    ],
    "data": [
        'wizard/invoice_add_phytosanitary.xml', 'views/account_invoice.xml',
        'views/phytosanitary.xml', 'views/product.xml', 'views/farm_campaign.xml',
        'views/res_partner_fields.xml', 'views/farm_notebook.xml', 'security/ir.model.access.csv',
        'security/security.xml', 'farm_notebook_report.xml', 'views/farm_notebook_report.xml'
    ],
}
