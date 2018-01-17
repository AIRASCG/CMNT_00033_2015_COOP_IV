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


class CowCount(models.Model):

    _name = 'cow.count'
    _order = 'date desc'

    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    date = fields.Date('Date')
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda r: r.env.user.id)
    heifer_0_3 = fields.Integer('Heifer 0-3 months',
                                states={'current': [('readonly', True)]})
    heifer_3_12 = fields.Integer('Heifer 3-12 months',
                                 states={'current': [('readonly', True)]})
    heifer_plus_12 = fields.Integer('Heifer >12 months',
                                    states={'current': [('readonly', True)]})
    milk_cow = fields.Integer('Milk cows',
                              states={'current': [('readonly', True)]})
    dry_cow = fields.Integer('Dry cows',
                             states={'current': [('readonly', True)]})
    state = fields.Selection(
        (('current', 'Current'), ('history', 'History')), 'State',
        default='history', readonly=True)
