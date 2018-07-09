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


class ResCompany(models.Model):

    _inherit = 'res.company'

    not_configured_accounting = fields.Boolean(
        'Configured accounting', compute="_get_not_configured_accounting")
    temporary = fields.Boolean('Temporary')
    with_complete_account = fields.Boolean('Install complete account')

    @api.one
    def _get_not_configured_accounting(self):
        fiscalyear = self.env['account.fiscalyear'].search(
            [('company_id', '=', self.id)])
        self.not_configured_accounting = not fiscalyear and True or False

    @api.multi
    def _launch_account_configure_wizards(self):
        self.ensure_one()
        wizard = self.env['account.installer'].create(
            {'charts': 'l10n_es', 'company_id': self.id, 'period': '3months'})
        wizard.action_next()

        pymes_chart = self.env.ref('l10n_es.account_chart_template_pymes')
        currency_id = pymes_chart.currency_id and \
            pymes_chart.currency_id.id or \
            self.env.user.company_id.currency_id.id
        wizard = self.env['wizard.multi.charts.accounts'].create(
            {'company_id': self.id, 'chart_template_id': pymes_chart.id,
             'code_digits': pymes_chart.code_digits,
             'currency_id': currency_id})
        wizard.action_next()

    @api.multi
    def configure_accounting(self):
        self.ensure_one()
        if not self.vat:
            raise exceptions.Warning(_(u"Debe escribir el cif en la explotación "
                                       "para poder configurar la contabilidad"))
        self._launch_account_configure_wizards()

        journal_sequence = self.env['ir.sequence'].create(
            {'name': _('Account move sequence'), 'company_id': self.id})
        journals = self.env['account.journal'].search(
            [('company_id', '=', self.id)])
        for journal in journals:
            write_vals = {'sequence_id': journal_sequence.id,
                          'update_posted': True}
            if journal.type in ('sale', 'sale_refund', 'purchase',
                                'purchase_refund'):
                write_vals['invoice_sequence_id'] = journal.sequence_id.id
            journal.write(write_vals)


class AccountAccountTemplate(models.Model):

    _inherit = 'account.account.template'

    @api.model
    def generate_account(self, chart_template_id, tax_template_ref,
                         acc_template_ref, code_digits, company_id):
        return super(AccountAccountTemplate,
                     self.with_context(company_configura=company_id)).generate_account(
            chart_template_id, tax_template_ref, acc_template_ref, code_digits, company_id)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('company_configura', False):
            company = self.env['res.company'].browse(self._context['company_configura'])
            if not company.with_complete_account:
                args = [('type', '!=', 'view')] + args
        return super(AccountAccountTemplate, self).search(
            args, offset=offset, limit=limit, order=order, count=count)



class WizardMultiChartsAccounts(models.TransientModel):

    _inherit='wizard.multi.charts.accounts'

    @api.model
    def _prepare_bank_account(self, line, new_code, acc_template_ref, ref_acc_bank, company_id):
        company = self.env['res.company'].browse(company_id)
        acc_template_ref_2 = acc_template_ref
        if not company.with_complete_account:
            if ref_acc_bank.id not in acc_template_ref_2:
                acc_template_ref_2[ref_acc_bank.id] = False
        return super(WizardMultiChartsAccounts, self)._prepare_bank_account(line, new_code, acc_template_ref, ref_acc_bank, company_id)

    @api.model
    def _prepare_all_journals(self, chart_template_id, acc_template_ref, company_id):
        res = super(WizardMultiChartsAccounts, self)._prepare_all_journals(chart_template_id, acc_template_ref, company_id)
        for journal_data in res:
            if journal_data['type'] == 'general':
                analytic_journal = self.env['account.analytic.journal'].search(
                    [('type', '=', 'general')], limit=1)
                journal_data['analytic_journal_id'] = analytic_journal.id
        return res
