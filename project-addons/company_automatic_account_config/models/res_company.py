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
