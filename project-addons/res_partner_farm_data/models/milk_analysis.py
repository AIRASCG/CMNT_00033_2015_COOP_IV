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

    analysis_id = fields.Many2one('milk.analysis', 'Analysis')
    sample_date = fields.Date('Sample date')
    dni = fields.Char('DNI')
    exploitation_name = fields.Char('Exploitation name')
    analysis_date = fields.Date('Analysis date')
    fat = fields.Float('Fat')
    protein = fields.Float('Protein')
    dry_extract = fields.Float('Dry extract')
    bacteriology = fields.Float('Bacteriology')
    cs = fields.Char('CS')
    inhibitors = fields.Float('Inhibitors')
    cryoscope = fields.Float('Cryoscope')
    urea = fields.Float('Urea')
    state = fields.Char('State')
    butyric = fields.Float('Butyric')
    water = fields.Float('Water')
    yearmonth = fields.Char('Year/month')
    route = fields.Float('Route')
    analysis_line_id = fields.Char('Id')

    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        res = super(MilkAnalysisLine, self).default_get(cr, uid, fields,
                                                        context=context)
        if context.get('analysis_id'):
            exploitation_id = context.get('analysis_id')
            res_partner_obj = self.pool.get('res.partner')
            res_partner_id = res_partner_obj.browse(cr, uid, exploitation_id)
            res.update({'exploitation_name': res_partner_id.name,
                        'dni': res_partner_id.vat})
        return res
