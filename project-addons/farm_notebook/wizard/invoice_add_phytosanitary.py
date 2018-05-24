# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _


class InvoiceAddPhytosanitary(models.TransientModel):

    _name = 'invoice.add.phytosanitary'

    total_qty = fields.Float()
    total_doses = fields.Float()
    uom = fields.Many2one('product.uom', required=True)
    registry_number = fields.Many2one('phytosanitary.registry.number', required=True)
    name = fields.Char(required=True)
    acquisition_date = fields.Date(required=True)
    invoice_line = fields.Many2one('account.invoice.line')

    @api.model
    def default_get(self, fields):
        res = super(InvoiceAddPhytosanitary, self).default_get(fields)

        invoice_line = self.env['account.invoice.line'].browse(self._context.get('active_id', False))
        res['invoice_line'] = invoice_line.id
        res['acquisition_date'] = invoice_line.invoice_id.date_invoice
        res['name'] = invoice_line.name
        return res

    @api.multi
    def confirm(self):
        self.env['phytosanitary'].create({
            'total_qty': self.total_qty,
            'total_doses': self.total_doses,
            'uom': self.uom.id,
            'registry_number': self.registry_number.id,
            'name': self.name,
            'acquisition_date': self.acquisition_date,
            'invoice_line': self.invoice_line.id,
        })
        return {'type': 'ir.actions.act_window_close'}
