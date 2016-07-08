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
from datetime import date

class ResCompany(models.Model):

    _inherit = 'res.company'

    @api.multi
    def open_fiscalyear(self, year):
        self.ensure_one()
        if self.env.user.id != 1:
            raise exceptions.Warning(_('Access error'), _('Only administrator can open fiscal year'))
        for company in self.search([('id', 'child_of', self.id)]):
            fiscalyear = self.env['account.fiscalyear'].search([('company_id', '=', company.id),('code', '=', year)])
            if fiscalyear:
                continue

            year_vals = {
                'name': year,
                'code': year,
                'company_id': company.id,
                'date_start': date(int(year), 01, 01),
                'date_stop': date(int(year), 12, 31),
            }
            new_fiscalyear = self.env['account.fiscalyear'].create(year_vals)
            new_fiscalyear.create_period3()
