# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "ERP xml data import",
    "summary": "",
    "version": "8.0.2.0.0",
    "category": "Uncategorized",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        'res_partner_farm_data'
    ],
    "data": [
        'views/document.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml'
    ],
}
