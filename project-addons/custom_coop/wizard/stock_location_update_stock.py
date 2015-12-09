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
from openerp import models, fields, api, tools, exceptions, _


class StockLocationUpdateStockWizard(models.TransientModel):

    _name = 'stock.location.update.stock.wizard'
    product_id = fields.Many2one('product.product', 'Product', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    quantity = fields.Float('Quantity')

    @api.multi
    def update(self):
        location_id = self._context.get('active_id', False)
        inventory_obj = self.env['stock.inventory']
        inventory_line_obj = self.env['stock.inventory.line']
        if self.quantity < 0:
            raise exceptions.Warning(_('Warning!'),
                                     _('Quantity cannot be negative.'))
        if self.product_id.id and self.lot_id.id:
            filter = 'none'
        elif self.product_id.id:
            filter = 'product'
        else:
            filter = 'none'
        inventory = inventory_obj.create({
            'name': _('INV: %s') % tools.ustr(self.product_id.name),
            'filter': filter,
            'product_id': self.product_id.id,
            'location_id': location_id,
            'lot_id': self.lot_id.id})
        product = self.product_id.with_context(location=location_id,
                                               lot_id=self.lot_id.id)
        th_qty = product.qty_available
        line_data = {
            'inventory_id': inventory.id,
            'product_qty': self.quantity,
            'location_id': location_id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'theoretical_qty': th_qty,
            'prod_lot_id': self.lot_id.id
        }
        inventory_line_obj.create(line_data)
        inventory.action_done()
        return {'type': 'ir.actions.act_window_close'}
