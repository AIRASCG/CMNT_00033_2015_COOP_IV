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

    def _get_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one('res.company', 'Company', required=True, default=_get_company)
    date = fields.Datetime('Date', required=True)
    exploitation_id = fields.Many2one('res.partner', 'Exploitation', required=True)
    state = fields.Selection(
        (('correct', 'Correct'), ('incorrect', 'Incorrect')), 'State')
    line_ids = fields.One2many('milk.analysis.line', 'analysis_id', 'Lines')

class MilkAnalysisLine(models.Model):

    _name = 'milk.analysis.line'

    analysis_id = fields.Many2one('milk.Analysis', 'Analysis')
    sample_date = fields.Date('Sample date')
    dni = fields.Char('DNI')
    exploitation_name = fields.Char('Exploitation name')
    analysis_date = fields.Date('Analysis date')
    fat = fields.Float('Fat')
    protein = fields.Float('Protein')
    dry_extract = fields.Float('Dry extract')
    bacteriology = fields.Float('Bacteriology')
    cs = fields.Float('CS')
    inhibitors = fields.Float('Inhibitors')
    cryoscope = fields.Float('Cryoscope')
    urea = fields.Float('Urea')
    state = fields.Char('State')
    butyric = fields.Float('Butyric')
    water = fields.Float('Water')
    yearmonth = fields.Char('Year/month')
    route = fields.Float('Route')
    analysis_line_id = fields.Char('Id')
