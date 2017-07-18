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

class AccountAccount(models.Model):

    _inherit = 'account.account'

    _parent_store = False


class AccountChartTemplate(models.Model):

    _inherit = 'account.chart.template'

    account_asset_id = fields.Many2one('account.account.template', '')
    account_depreciation_id = fields.Many2one('account.account.template', '')
    account_expense_depreciation_id = fields.Many2one(
        'account.account.template', '')
    account_deterioration_depreciation_id = fields.Many2one('account.account.template', '')
    account_deterioration_expense_depreciation_id = fields.Many2one('account.account.template', '')


class WizardMultiChartsAccounts(models.TransientModel):

    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def generate_properties(self, chart_template_id, acc_template_ref,
                            company_id):
        todo_list = [
            ('account_asset_id', 'account.asset.category', 'account.account'),
            ('account_depreciation_id', 'account.asset.category',
             'account.account'),
            ('account_expense_depreciation_id', 'account.asset.category',
             'account.account'),
            ('account_deterioration_depreciation_id', 'account.asset.category',
             'account.account'),
            ('account_deterioration_expense_depreciation_id', 'account.asset.category',
             'account.account'),
            ('journal_id', 'account.asset.category',
             'account.journal'),
        ]
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        template = self.env['account.chart.template'].browse(chart_template_id)
        for record in todo_list:
            if record[2] == 'account.account':
                account = getattr(template, record[0])
                value = account and 'account.account,' + \
                    str(acc_template_ref[account.id]) or False
            else:
                journal = self.env['account.journal'].search([('code', '=', 'ACT'), ('company_id', '=', company_id)])
                value = journal and 'account.journal,' + str(journal.id) or False
            if value:
                field = field_obj.search([('name', '=', record[0]),
                                          ('model', '=', record[1]),
                                          ('relation', '=', record[2])])
                vals = {
                    'name': record[0],
                    'company_id': company_id,
                    'fields_id': field[0].id,
                    'value': value,
                }
                properties = property_obj.search([('name', '=', record[0]),
                                                  ('company_id', '=',
                                                   company_id)])
                if properties:
                    #the property exist: modify it
                    properties.write(vals)
                else:
                    #create the property
                    property_obj.create(vals)
        return super(WizardMultiChartsAccounts, self).generate_properties(
            chart_template_id, acc_template_ref, company_id)

    @api.model
    def _prepare_all_journals(self, chart_template_id, acc_template_ref,
                              company_id):
        res = super(WizardMultiChartsAccounts, self)._prepare_all_journals(
            chart_template_id, acc_template_ref, company_id)
        res.append({
            'type': 'general',
            'name': _('Assets journal'),
            'code': 'ACT',
            'company_id': company_id,
        })
        return res


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    date_invoice = fields.Date(related='invoice_id.date_invoice')
    partner_id = fields.Many2one('res.partner',
                                 related='invoice_id.partner_id')
    allowed_analytic_plans = fields.Many2many(
        'account.analytic.plan.instance', compute='_compute_allowed_analytic_plans')

    @api.depends('product_id')
    def _compute_allowed_analytic_plans(self):
        for line in self:
            if line.product_id:
                line.allowed_analytic_plans = self.env['account.analytic.plan.instance'].search(
                    ['|', ('allowed_products', '=', line.product_id.id),
                     ('allowed_products', '=', False)])
