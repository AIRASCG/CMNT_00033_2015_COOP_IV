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


class AccountAnalyticReportTemplate(models.Model):

    _name = 'account.analytic.report.template'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    line_ids = fields.One2many('account.analytic.report.template.line', 'template_id', 'Lines')


class AccountAnalyticReportTemplateLine(models.Model):
    _name = 'account.analytic.report.template.line'

    template_id = fields.Many2one('account.analytic.report.template', 'Template',
                                  default=lambda self: self._context.get('template_id', None))
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('sequence', default=10)
    name = fields.Char('Name', required=True)
    value_1 = fields.Text('Value 1')
    value_2 = fields.Text('Value 2')
    parent_id = fields.Many2one('account.analytic.report.template.line', 'Parent',
                                ondelete='cascade')
    child_ids = fields.One2many('account.analytic.report.template.line', 'parent_id', 'Childs')
    css_style = fields.Selection(
        [('red_bold', 'Red bold'), ('green_bold', 'Green bold'), ('bold', 'Bold'), ('red', 'Red')],
        'Css style')

    _order = "sequence, code"

    _sql_constraints = [
        ('report_code_uniq', 'unique(template_id, code)',
         _("The code must be unique for this report!"))
    ]
