# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea All Rights Reserved
#    $Carlos Lombardía Rodríguez <carlos@comunitea.com>$
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

class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.model
    def create(self, vals):
        if not vals.get('parent_id', False) and vals.get('type', False) != 'contract':
            if self.env.user.id != 1:
                raise exceptions.Warning(_('Create error'), _('Unauthorized user'))
        return super(AccountAnalyticAccount, self).create(vals)


class AccountAnalyticJournal(models.Model):
    _inherit = 'account.analytic.journal'

    company_id = fields.Many2one('res.company', 'Company', required=False,
                                 default=False)


class AccountAnalyticPlanInstance(models.Model):

    _inherit = 'account.analytic.plan.instance'

    allowed_products = fields.Many2many(
        'product.product',
        'analytic_plan_product_rel',
        'plan_id',
        'product_id')

    @api.model
    def create(self, vals):
        if self._context.get('product_id'):
            if 'allowed_products' not in vals:
                vals['allowed_products'] = []
            vals['allowed_products'].append((4, self._context.get('product_id')))
        return super(AccountAnalyticPlanInstance, self).create(vals)
