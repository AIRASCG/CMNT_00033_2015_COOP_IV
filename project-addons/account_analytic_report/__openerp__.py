# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account analytic report',
    'version': '1.0',
    'category': 'Account',
    'description': """""",
    'author': 'Comunitea',
    'website': '',
    "depends": ['account', 'custom_report', 'farm_notebook'],
    "data": ['views/account_analytic_report_template.xml',
             'views/account_analytic_report.xml',
             'views/account_analytic_report_menu.xml',
             'security/ir.model.access.csv',
             'views/report_account_analytic_report.xml',
             'qweb_analytic_report.xml', 'data/pyg_1000.xml',
             'data/pyg_cow.xml', 'data/pyg_employee.xml',
             'security/security.xml', 'data/pyg_ha.xml',
             'data/technical_economic.xml', 'data/recria.xml',
             'data/commercial_report.xml'],
    "installable": True
}
