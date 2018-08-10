# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            milk_lines = invoice.invoice_line.filtered(
                lambda r: r.product_id.is_milk_quota)
            if milk_lines:
                quota = self.env['output.quota'].search(
                    [('year_id', '=', invoice.period_id.fiscalyear_id.id),
                     ('farm_id', '=', invoice.company_id.partner_id.id)])
                if quota:
                    if invoice.type == 'out_invoice':
                        quota.value += sum(milk_lines.mapped('quantity'))
                    else:
                        quota.value -= sum(milk_lines.mapped('quantity'))
        return res

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            milk_lines = invoice.invoice_line.filtered(
                lambda r: r.product_id.is_milk_quota)
            if milk_lines:
                quota = self.env['output.quota'].search(
                    [('year_id', '=', invoice.period_id.fiscalyear_id.id),
                     ('farm_id', '=', invoice.company_id.partner_id.id)])
                if quota:
                    if invoice.type == 'out_invoice':
                        quota.value -= sum(milk_lines.mapped('quantity'))
                    else:
                        quota.value += sum(milk_lines.mapped('quantity'))
        return res
