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
from openerp import models
from openerp.osv import fields
import openerp.addons.decimal_precision as dp


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company')
    }


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    def _debit_credit_bal_qtty(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        if context is None:
            context = {}
        child_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)]))
        for i in child_ids:
            res[i] =  {}
            for n in fields:
                res[i][n] = 0.0

        if not child_ids:
            return res

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args  += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]
        if context.get('campaign', False):
            where_date += " AND l.campaign = %s"
            where_clause_args += [context['campaign']]
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            user = self.pool.get('res.users').browse(cr, uid, uid, context)
            company_id = user.company_id.id
        companies = self.pool.get('res.company').search(cr, uid, [('id', 'child_of', company_id)], context=context)
        where_clause_args += [tuple(companies)]
        cr.execute(("""
              SELECT a.id,
                     sum(
                         CASE WHEN l.amount > 0
                         THEN l.amount
                         ELSE 0.0
                         END
                          ) as debit,
                     sum(
                         CASE WHEN l.amount < 0
                         THEN -l.amount
                         ELSE 0.0
                         END
                          ) as credit,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date + """ AND l.company_id IN %s
              GROUP BY a.id"""), where_clause_args)
        for row in cr.dictfetchall():
            res[row['id']] = {}
            for field in fields:
                res[row['id']][field] = row[field]
        return self._compute_level_tree(cr, uid, ids, child_ids, res, fields, context)

    _columns = {
        'balance': fields.function(_debit_credit_bal_qtty, type='float', string='Balance', multi='debit_credit_bal_qtty', digits_compute=dp.get_precision('Account')),
        'debit': fields.function(_debit_credit_bal_qtty, type='float', string='Debit', multi='debit_credit_bal_qtty', digits_compute=dp.get_precision('Account')),
        'credit': fields.function(_debit_credit_bal_qtty, type='float', string='Credit', multi='debit_credit_bal_qtty', digits_compute=dp.get_precision('Account')),
        'quantity': fields.function(_debit_credit_bal_qtty, type='float', string='Quantity', multi='debit_credit_bal_qtty'),

    }
