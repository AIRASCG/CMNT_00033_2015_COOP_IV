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


class AccountAssetCategory(models.Model):

    _inherit = 'account.asset.category'

    journal_id = fields.Many2one(company_dependent=True)
    account_asset_id = fields.Many2one(company_dependent=True)
    account_depreciation_id = fields.Many2one(company_dependent=True)
    account_expense_depreciation_id = fields.Many2one(company_dependent=True)
    account_deterioration_depreciation_id = fields.Many2one(
        'account.account', 'Deterioration depreciation account',
        company_dependent=True)
    account_deterioration_expense_depreciation_id = fields.Many2one(
        'account.account', 'Deterioration depr. expense dccount',
        company_dependent=True)
    subvention_analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Subvention analytic account')
    analytic_plan = fields.Many2one('account.analytic.plan.instance',
                                    'Analytic plan')
    subvention_analytic_plan = fields.Many2one(
        'account.analytic.plan.instance', 'Subvention Analytic plan')
    company_id = fields.Many2one(required=False)


class AccountAssetAsset(models.Model):

    _inherit = 'account.asset.asset'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', 'Analytic account',
        states={'draft': [('readonly', False)], 'open': [('readonly', True)],
                'close': [('readonly', True)]})
    analytic_plan = fields.Many2one(
        'account.analytic.plan.instance', 'Analytic plan',
        states={'draft': [('readonly', False)], 'open': [('readonly', True)],
                'close': [('readonly', True)]})
    subvention = fields.Boolean('Subvention',
                                states={'draft': [('readonly', False)],
                                        'open': [('readonly', True)],
                                        'close': [('readonly', True)]})

    @api.multi
    def onchange_category_id_subvention(self, category_id, subvention):
        res = super(AccountAssetAsset, self).onchange_category_id(category_id)
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            if subvention:
                res['value']['account_analytic_id'] = category.subvention_analytic_account_id.id
                res['value']['analytic_plan'] = category.subvention_analytic_plan.id
            else:
                res['value']['account_analytic_id'] = category.account_analytic_id.id
                res['value']['analytic_plan'] = category.analytic_plan.id
        return res

    @api.onchange('subvention')
    @api.one
    def onchange_subvention(self):
        if self.category_id:
            if self.subvention:
                analytic_acc = self.category_id.subvention_analytic_account_id
                self.account_analytic_id = analytic_acc
                self.analytic_plan = self.category_id.subvention_analytic_plan
            else:
                self.account_analytic_id = self.category_id.account_analytic_id
                self.analytic_plan = self.category_id.analytic_plan

    @api.multi
    def set_to_close(self):
        for asset in self:
            depreciation_lines = asset.depreciation_line_ids
            if depreciation_lines.filtered(lambda a: not a.move_check):
                asset.create_deterioration_move()
        return super(AccountAssetAsset, self).set_to_close()

    @api.multi
    def create_deterioration_move(self):
        self.ensure_one()
        total = sum([x.amount for x in self.depreciation_line_ids
                     if not x.move_check])
        category = self.category_id
        depreciation_date = time.strftime('%Y-%m-%d')
        period_ids = self.env['account.period'].find(depreciation_date)
        company_currency = self.company_id.currency_id.id
        current_currency = self.currency_id.id
        amount = self.currency_id.compute(total, self.company_id.currency_id)
        sign = (category.journal_id.type == 'purchase' and 1) or -1
        asset_name = "/"
        reference = self.name
        move_vals = {
            'name': asset_name,
            'date': depreciation_date,
            'ref': reference,
            'period_id': period_ids and period_ids[0].id or False,
            'journal_id': category.journal_id.id,
        }
        move = self.env['account.move'].create(move_vals)
        journal_id = category.journal_id.id
        partner_id = self.partner_id.id
        self.env['account.move.line'].create({
            'name': asset_name,
            'ref': reference,
            'move_id': move.id,
            'account_id': category.account_deterioration_depreciation_id.id,
            'debit': 0.0,
            'credit': amount,
            'period_id': period_ids and period_ids[0].id or False,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'currency_id': company_currency != current_currency and
            current_currency or False,
            'amount_currency': company_currency != current_currency and
            - sign * total or 0.0,
            'date': depreciation_date,
        })
        exp_account = category.account_deterioration_expense_depreciation_id
        self.env['account.move.line'].create({
            'name': asset_name,
            'ref': reference,
            'move_id': move.id,
            'account_id': exp_account.id,
            'credit': 0.0,
            'debit': amount,
            'period_id': period_ids and period_ids[0].id or False,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'currency_id': company_currency != current_currency and
            current_currency or False,
            'amount_currency':
            company_currency != current_currency and sign * total or 0.0,
            'analytic_account_id': category.account_analytic_id.id,
            'date': depreciation_date,
            'asset_id': self.id
        })
        self.depreciation_line_ids.filtered(lambda a: not a.move_check).write(
            {'move_id': move.id})
        if move.journal_id.entry_posted:
            move.button_cancel()
        for move_line in move.line_id:
            write_vals = {}
            if move_line.debit:
                if self.analytic_plan:
                    write_vals.update({'analytics_id':
                                       self.analytic_plan.id,
                                       'analytic_account_id': False})
                else:
                    write_vals.update({'analytic_account_id':
                                       self.account_analytic_id.id})
            if self.subvention:
                debit = move_line.debit
                credit = move_line.credit
                write_vals.update({'debit': credit, 'credit': debit})
            if write_vals:
                move_line.write(write_vals)
        if move.journal_id.entry_posted:
            move.button_validate()
        if self.currency_id.is_zero(self.value_residual):
            self.write({'state': 'close'})


class AccountAssetDepreciationLine(models.Model):

    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self):
        all_moves = []
        for line in self:
            asset = line.asset_id
            move_id = super(AccountAssetDepreciationLine, line).create_move()
            all_moves += move_id
            move = self.env['account.move'].browse(move_id[0])
            if move.journal_id.entry_posted:
                move.button_cancel()
            for move_line in move.line_id:
                write_vals = {}
                if move_line.debit:
                    if asset.analytic_plan:
                        write_vals.update({'analytics_id':
                                           asset.analytic_plan.id,
                                           'analytic_account_id': False})
                    else:
                        write_vals.update({'analytic_account_id':
                                           asset.account_analytic_id.id})
                if asset.subvention:
                    debit = move_line.debit
                    credit = move_line.credit
                    write_vals.update({'debit': credit, 'credit': debit})
                if write_vals:
                    move_line.write(write_vals)
            if move.journal_id.entry_posted:
                move.button_validate()
        return all_moves
