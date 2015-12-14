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


class AccountAssetAsset(models.Model):

    _inherit = 'account.asset.asset'

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          'Analytic account',
                                          states={'draft': [('readonly', False)],
                                                  'open': [('readonly', True)],
                                                  'close': [('readonly', True)]})
    subvention = fields.Boolean('Subvention',
                                states={'draft': [('readonly', False)],
                                        'open': [('readonly', True)],
                                        'close': [('readonly', True)]})

    @api.multi
    def onchange_category_id(self, category_id):
        res = super(AccountAssetAsset, self).onchange_category_id(category_id)
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            res['value']['account_analytic_id'] = category.account_analytic_id.id
        return res


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
                if move_line.debit:
                    write_vals = {'analytic_account_id':
                                  asset.account_analytic_id.id}
                if asset.subvention:
                    debit = move_line.debit
                    credit = move_line.credit
                    write_vals.update({'debit': credit, 'credit': debit})
                if write_vals:
                    move_line.write(write_vals)
            if move.journal_id.entry_posted:
                move.button_validate()
        return all_moves
