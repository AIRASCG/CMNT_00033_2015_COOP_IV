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
from . import custom_models
from openerp import fields, api, exceptions, _


class EmployeeFarmCount(custom_models.HistoricalModel):

    _name = 'employee.farm.count'
    _order = 'sequence desc'

    sequence = fields.Integer('sequence', default=0)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    date = fields.Date('Date', states={'current': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    quantity = fields.Integer('Employees',
                              states={'current': [('readonly', True)]})
    state = fields.Selection(
        (('current', 'Current'), ('history', 'History')), 'State',
        default='current', readonly=True)
