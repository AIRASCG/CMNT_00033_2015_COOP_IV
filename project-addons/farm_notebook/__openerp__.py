# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Farm notebook',
    'summary': '',
    'version': '8.0.2.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'res_partner_farm_data',
        'product',
        'account',
        'account_analytic_plans',
        'custom_report'
    ],
    'data': [
        'wizard/phytosanitary_add_campaign_wizard.xml',
        'wizard/invoice_add_phytosanitary.xml', 'views/account_invoice.xml',
        'views/phytosanitary.xml', 'views/product.xml',
        'wizard/farm_campaign_add_fields.xml',
        'views/farm_campaign.xml', 'views/res_partner.xml',
        'views/res_partner_fields.xml', 'views/farm_notebook.xml',
        'security/ir.model.access.csv', 'security/security.xml',
        'farm_notebook_report.xml', 'views/farm_notebook_report.xml'
    ],
}
