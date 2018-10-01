# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    quota = fields.Many2one('output.quota', 'Quota')

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            milk_lines = invoice.invoice_line.filtered(
                lambda r: r.product_id.is_milk_quota)
            if milk_lines:
                if invoice.type == 'out_invoice':
                    quota_value = sum(milk_lines.mapped('quantity')) * \
                        1000.0
                else:
                    quota_value = -sum(milk_lines.mapped('quantity')) * \
                        1000.0
                quota = self.env['output.quota'].\
                    create({'year_id': invoice.period_id.fiscalyear_id.id,
                            'farm_id': invoice.company_id.partner_id.id,
                            'date': invoice.date_invoice,
                            'value': quota_value})
                invoice.quota = quota

        return res

    @api.multi
    def action_cancel(self):
        for invoice in self.filtered(lambda x: x.state == 'open'):
            if self.quota:
                self.quota.unlink()
        return super(AccountInvoice, self).invoice_validate()
