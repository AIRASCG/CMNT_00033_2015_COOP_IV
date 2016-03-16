# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
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


class MilkControl(models.Model):

    _name = 'milk.control'

    date = fields.Datetime('Date', required=True)
    exploitation_id = fields.\
        Many2one('res.partner', 'Exploitation', required=True,
                 default=lambda self: self.env.user.company_id.partner_id.id)
    state = fields.Selection(
        (('correct', 'Correct'), ('incorrect', 'Incorrect')), 'State')
    company_id = fields.Many2one("res.company", readonly=True,
                                 related="exploitation_id.company_id")
    line_ids = fields.One2many('milk.control.line', 'control_id', 'Lines')
    num_records = fields.Integer('Number of records', compute = '_get_num_records')
    exception_txt = fields.Text("Exceptions", readonly=True)

    @api.multi
    def _get_num_records(self):
        for obj in self:
            obj.num_records = len(obj.line_ids)

class MilkControlLine(models.Model):

    _name = 'milk.control.line'

    control_id = fields.Many2one('milk.control', 'Control')
    cea = fields.Char('CEA')
    cib = fields.Char('CIB')
    crotal = fields.Char('crotal corto')
    name = fields.Char('Name')
    date_birth = fields.Date('Date of birth')
    birth_number = fields.Integer('Number of births')
    control_number = fields.Integer('Number of controls')
    days = fields.Integer('DEL')
    milk_liters = fields.Float('Milk liters')
    fat = fields.Float('Fat %')
    protein = fields.Float('Protein %')
    rcs = fields.Integer('RCS')
    urea = fields.Integer('Urea')
    cumulative_milk = fields.Integer('')
    cumulative_fat = fields.Float('')
    cumulative_protein = fields.Float('')