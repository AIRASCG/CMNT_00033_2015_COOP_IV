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
    'name': 'Automatic company configuration',
    'version': '1.0',
    'category': '',
    'description': """This module adds a wizard that configure automatically the account""",
    'author': 'Comunitea',
    'website': '',
    "depends": ['base', 'account', 'l10n_es', 'account_cancel',
                'l10n_es_account_invoice_sequence', 'company_assign_users'],
    "data": ['views/res_company.xml'],
    "installable": True
}
