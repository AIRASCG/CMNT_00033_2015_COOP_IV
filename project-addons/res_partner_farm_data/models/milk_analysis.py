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
from openerp import models, fields, api, tools, _
from calendar import monthrange, month_name


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
    num_records = fields.Integer('Number of records',
                                 compute='_get_num_records')
    exception_txt = fields.Text("Exceptions", readonly=True)

    @api.multi
    def _get_num_records(self):
        for obj in self:
            obj.num_records = len(obj.line_ids)


class MilkAnalysisLine(models.Model):

    _name = 'milk.analysis.line'

    analysis_id = fields.Many2one('milk.analysis', 'Analysis',
                                  ondelete='cascade')
    analysis_line_id = fields.Char('Id')
    route = fields.Float('Route')
    yearmonth = fields.Char('Year/month')
    sample_date = fields.Date('Sample date')
    reception_date = fields.Date('Reception date')
    analysis_date = fields.Date('Analysis date')
    state = fields.Selection((('accepted', 'Accepted'),
                              ('rejected', 'Rejected'),
                              ('waiting', 'Waiting')), 'State')
    fat = fields.Float('Fat')
    protein = fields.Float('Protein')
    dry_extract = fields.Float('Dry extract')
    bacteriology = fields.Char('Bacteriology')
    cs = fields.Char('CS')
    inhibitors = fields.Char('Inhibitors')
    cryoscope = fields.Float('Cryoscope')
    urea = fields.Char('Urea')


class MilkAnalysisReport(models.Model):

    _name = 'milk.analysis.report'
    _auto = False

    exploitation_id = fields.Many2one('res.partner')
    date = fields.Date()
    state = fields.Selection((('accepted', 'Accepted'),
                              ('rejected', 'Rejected'),
                              ('waiting', 'Waiting')))
    fat = fields.Float()
    protein = fields.Float()
    dry_extract = fields.Float()
    bacteriology = fields.Char()
    cs = fields.Char('CS')
    inhibitors = fields.Char()
    cryoscope = fields.Float()
    urea = fields.Float()

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE VIEW milk_analysis_report as(
SELECT l.fat as fat, l.protein as protein, l.dry_extract as dry_extract,
       l.bacteriology as bacteriology, l.cs as cs, l.inhibitors as inhibitors,
       l.cryoscope as cryoscope, l.urea as urea, l.sample_date as date,
       m.exploitation_id as exploitation_id, l.id as id, l.state as state
FROM milk_analysis_line l join milk_analysis m on l.analysis_id = m.id
)""")


class MilkAnalysisMonthReport(models.Model):

    _name = 'milk.analysis.month.report'
    _auto = False
    _order = 'date asc'

    exploitation_id = fields.Many2one('res.partner')
    date = fields.Char()
    year = fields.Char(compute='_get_date')
    month = fields.Char(compute='_get_date')
    month_name = fields.Char(compute='_get_date')
    fat = fields.Float()
    protein = fields.Float()
    dry_extract = fields.Float()
    bacteriology = fields.Char(compute='_get_bacteriology')
    cs = fields.Char('CS', compute='_get_bacteriology')

    def _get_date(self):
        for l in self:
            l.year = l.date[:4]
            l.month = l.date[5:]
            l.month_name = month_name[int(l.date[5:])]

    def _get_bacteriology(self):
        for l in self:
            month = int(l.month)
            year = int(l.year)
            analysis = self.env['milk.analysis.line'].search(
                [('analysis_id.exploitation_id', '=', l.exploitation_id.id),
                 ('sample_date', '>=', '%s-%s-01' % (year, month)),
                 ('sample_date', '<=', '%s-%s-%s' %
                  (year, month, monthrange(year, month)[1])),
                 ])
            try:
                bacteriology = sum(
                    [float(x.bacteriology) for x in analysis]) / len(analysis)
                l.bacteriology = str(round(bacteriology, 2))
            except ValueError:
                l.bacteriology = '-'
            try:
                cs = sum([float(x.cs) for x in analysis]) / len(analysis)
                l.cs = str(round(cs, 2))
            except ValueError:
                l.cs = '-'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)

        cr.execute("""CREATE VIEW milk_analysis_month_report as(
SELECT ROW_NUMBER() OVER() AS id,
       m.exploitation_id as exploitation_id,
       avg(l.fat) as fat,
       avg(l.protein) as protein,
       avg(l.dry_extract) as dry_extract,
       to_char(l.sample_date, 'YYYY-MM') as date
FROM milk_analysis_line l
     JOIN milk_analysis m ON l.analysis_id = m.id
GROUP BY m.exploitation_id, to_char(l.sample_date, 'YYYY-MM')
)""")
