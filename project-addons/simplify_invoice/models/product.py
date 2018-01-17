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
from openerp import models, fields, exceptions, api, _


class ProductProduct(models.Model):

    _inherit = 'product.product'

    analytic_default_ids = fields.One2many('account.analytic.default',
                                           'product_id', 'Analityc defaults')

    @api.constrains('type', 'analytic_default_ids')
    def required_analytic_default_ids(self):
        for prod in self:
            if prod.type == 'service' and not prod.analytic_default_ids:
                raise exceptions.ValidationError(
                    _('Plan analítico por defecto requerido'))
