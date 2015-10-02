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


class CostImputation(models.Model):

    _name = 'cost.imputation'

    @api.model
    def _get_user_id(self):
        return self.env.user.id

    farm_id = fields.Many2one('res.partner', 'Farm', required=True)
    user_id = fields.Many2one('res.users', 'User', default=_get_user_id,
                              required=True)
    date = fields.Date('Date',
                       default=lambda *a: date.today().strftime('%Y-%m-%d'),
                       required=True)
    type_id = fields.Many2one('product.product', 'Type', required=True)
    state = fields.Selection(
        (('current', 'Current'), ('old', 'Old')), 'State', default='current')
    year_id = fields.Many2one('account.fiscalyear', 'Year', required=True)
    value_id = fields.Many2one('account.analytic.plan.instance', 'Value',
                               required=True)

    @api.onchange('farm_id')
    def onchange_farm_id(self):
        company = self.env['res.company'].search([('partner_id', '=',
                                                   self.farm_id.id)])
        if not company:
            self.year_id = False
        curdate = date.today().strftime('%Y-%m-%d')
        year = self.env['account.fiscalyear'].search(
            [('date_start', '<=', curdate), ('date_stop', '>=', curdate),
             ('company_id', '=', company.id)])
        year.write({'state': 'done'})
        self.year_id = year
