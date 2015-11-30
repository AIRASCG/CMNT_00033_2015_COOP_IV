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
from openerp import models, fields, api, exceptions, _
from datetime import date, timedelta


class ResCompany(models.Model):

    _inherit = 'res.company'

    @api.model
    def calc_assets(self):
        for company in self.search([]):
            td = date.today()
            last_month = date(td.year, td.month - 1, 1)
            period = self.env['account.period'].search(
                [('date_start', '<=', last_month), ('date_stop', '>=', last_month),
                 ('company_id', '=', company.id)])
            if period:
                assets = self.env['account.asset.asset'].search([('state', '=', 'open'),
                                                                 ('company_id', '=',
                                                                  company.id)])
                assets.with_context(company_id=company.id)._compute_entries(period.id)
