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


class StockLocation(models.Model):

    _inherit = 'stock.location'

    @api.model
    def _get_default_location(self):
        return self.env.ref('stock.stock_location_locations').id

    location_id = fields.Many2one(default=_get_default_location)

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    stock_available = fields.Float(string="Stock available",
                                   compute="_compute_stock_available",
                                   readonly=True)

    @api.one
    @api.depends("stock_available")
    def _compute_stock_available(self):
        sum_quants = 0.0
        for quant in self.quant_ids:
            if self.quant_ids.location_id.usage == u'internal':
                sum_quants += self.quant_ids.qty
        self.stock_available = sum_quants
