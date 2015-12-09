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
import time


class AccountAnalyticReport(models.Model):

    _name = 'account.analytic.report'

    name = fields.Char('Name', required=True)
    template_id = fields.Many2one('account.analytic.report.template', 'Template',
                                  required=True)

    calc_date = fields.Date('Calc date')
    ref_1 = fields.Reference(selection=[('res.company', 'Company'), ('res.partner.category', 'Farm group')], string='Reference')
    from_date_1 = fields.Date('From date')
    to_date_1 = fields.Date('To date')
    ref_2 = fields.Reference(selection=[('res.company', 'Company'), ('res.partner.category', 'Farm group')], string='Reference')
    from_date_2 = fields.Date('From date')
    to_date_2 = fields.Date('To date')

    line_ids = fields.One2many('account.analytic.report.line', 'report_id', 'Lines')
    state = fields.Selection(
        (('draft', 'Draft'), ('calc', 'Calculating'), ('calc_done', 'Calculated'),
         ('done', 'Done'), ('cancel', 'Cancel')), 'State', default='draft')

    @api.multi
    def _get_companies(self, company_1_2=1):
        self.ensure_one()
        companies = self.env['res.company']
        ref_field = 'ref_%s' % str(company_1_2)
        if not self[ref_field]:
            return companies
        if 'res.company' == str(self[ref_field]._model):
            companies = self[ref_field]
        elif 'res.partner.category' == str(self[ref_field]._model):
            partners = self.env['res.partner'].search([('category_id', '=', self[ref_field].id)])
            companies = partners.filtered(lambda partner: partner.farm).mapped('company_id')
        return companies

    @api.one
    def refresh_values(self):
        field = 'val_%s' % str(1)
        for line in self.line_ids:
            companies = self._get_companies(1)
            line.value_1 = sum([line.get_value_1(x) for x in companies])
            companies = self._get_companies(2)
            line.value_2 = sum([line.get_value_2(x) for x in companies])

    @api.multi
    def act_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def act_done(self):
        self.write({'state': 'done'})

    @api.multi
    def calculate(self):
        self.write({
            'state': 'calc',
            'calc_date': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self.line_ids.unlink()
        for line in self.template_id.line_ids:
            self.env['account.analytic.report.line'].create({
                'report_id': self.id,
                'code': line.code,
                'sequence': line.sequence,
                'name': line.name,
                'notes': '',
                'template_line_id': line.id,
            })
        for line in self.line_ids:
            if line.template_line_id.parent_id:
                parent_line = self.env['account.analytic.report.line'].search(
                    [('template_line_id', '=', line.template_line_id.parent_id.id),
                     ('report_id', '=', self.id)])
                line.parent_id = parent_line
        self.refresh_values()
        self.state = 'calc_done'


class AccountAnalyticReportLine(models.Model):

    _name = 'account.analytic.report.line'

    report_id = fields.Many2one('account.analytic.report', 'report')
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('sequence', default=10)
    name = fields.Char('Name', required=True)
    notes = fields.Text('Notes')
    value_1 = fields.Text('Value 1')
    value_2 = fields.Text('Value 2')
    template_line_id = fields.Many2one('account.analytic.report.template.line',
                                       'Template line')
    parent_id = fields.Many2one('account.analytic.report.line', 'Parent')
    child_ids = fields.One2many('account.analytic.report.line', 'parent_id', 'Childs')

    @api.multi
    def get_value_1(self, company):
        return self.eval_line(company, 'value_1')

    @api.multi
    def get_value_2(self, company):
        return self.eval_line(company, 'value_2')

    @api.multi
    def eval_line(self, company, field):
        self.ensure_one()
        if not self.template_line_id[field]:
            return sum([x.eval_line(company, field) for x in self.child_ids])
        vals = self.template_line_id[field].replace(' ', '').split(',')
        final_vals = []
        for val in vals:
            sign = '-'
            if val[0] != '-':
                sign = '+'
                val = '+' + val
            if val[1] == '.':  # Se referencia a otra linea
                code_line = val.replace('.', '')[1:]
                line = self.search([('report_id', '=', self.report_id.id), ('code', '=', code_line)])
                if not line:
                    raise exceptions.Warning(_('Line not found'),
                                             _('Line with code %s not found') % code_line)
                val = sign + str(line.eval_line(company, field))
            elif val[1] == "'": # Valor literal
                val = val.replace("'", "")
            else:  # se referencia a una cuenta
                account = self.env['account.analytic.account'].search([('code', '=', val[1:])])
                if not account:
                    raise exceptions.Warning(_('Account not found'),
                                             _('Account with code %s not found') % val[1:])
                from_date = self.report_id.from_date_1
                to_date = self.report_id.to_date_1
                val = sign + str(account.with_context(company_id=company.id,from_date=from_date,to_date=to_date).balance)
            final_vals.append(val)
        return eval(''.join(final_vals))
