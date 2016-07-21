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


class MilkAnalysis(models.Model):

    _name = 'milk.analysis'

    date = fields.Datetime('Date', required=True)
    exploitation_id = fields.\
        Many2one('res.partner', 'Exploitation', required=True,
                 default=lambda self: self.env.user.company_id.partner_id.id)
    company_id = fields.Many2one("res.company", readonly=True,
                                 related="exploitation_id.company_id")
    state = fields.Selection(
        (('correct', 'Correct'), ('incorrect', 'Incorrect')), 'State')
    line_ids = fields.One2many('milk.analysis.line', 'analysis_id', 'Lines')
    num_records = fields.Integer('Number of records', compute = '_get_num_records')
    exception_txt = fields.Text("Exceptions", readonly=True)

    @api.multi
    def _get_num_records(self):
        for obj in self:
            obj.num_records = len(obj.line_ids)

class MilkAnalysisLine(models.Model):

    _name = 'milk.analysis.line'

    analysis_id = fields.Many2one('milk.analysis', 'Analysis', ondelete='cascade')
    analysis_line_id = fields.Char('Id')
    route = fields.Float('Route')
    yearmonth = fields.Char('Year/month')
    sample_date = fields.Date('Sample date')
    reception_date = fields.Date('Reception date')
    analysis_date = fields.Date('Analysis date')
    state = fields.Selection((('accepted', 'Accepted'), ('rejected', 'Rejected'), ('waiting', 'Waiting')), 'State')
    fat = fields.Float('Fat')
    protein = fields.Float('Protein')
    dry_extract = fields.Float('Dry extract')
    bacteriology = fields.Char('Bacteriology')
    cs = fields.Float('CS')
    inhibitors = fields.Char('Inhibitors')
    cryoscope = fields.Float('Cryoscope')
    urea = fields.Float('Urea')
