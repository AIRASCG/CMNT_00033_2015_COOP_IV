# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    phytosanitary = fields.Boolean(related='product_id.phytosanitary')
    phytosanitary_created = fields.Boolean(
        compute='_compute_phytosanitary_created')
    campaign = fields.Many2one('farm.campaign')

    @api.multi
    def _compute_phytosanitary_created(self):
        for line in self:
            if line.phytosanitary:
                phyto = self.env['phytosanitary'].search(
                    [('invoice_line', '=', line.id)])
                if phyto:
                    line.phytosanitary_created = True
                    continue

            line.phytosanitary_created = False

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        res['campaign'] = line.campaign and line.campaign.id or False
        return res


class AccountAnalyticPlanInstanceLine(models.Model):

    _inherit = 'account.analytic.plan.instance.line'

    campaign = fields.Many2one('farm.campaign')


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    campaign = fields.Many2one('farm.campaign')


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    campaign = fields.Many2one('farm.campaign')

    @api.model
    def _prepare_analytic_line(self, obj_line):
        res = super(AccountMoveLine, self)._prepare_analytic_line(obj_line)
        res['campaign'] = obj_line.campaign and obj_line.campaign.id or False
        return res

    @api.multi
    def create_analytic_lines(self):
        # Se vuelven a eliminar y crear las lineas analiticas para añadir
        # la campaña igual que en account_analytic_plans
        super(AccountMoveLine, self).create_analytic_lines()
        analytic_line_obj = self.env['account.analytic.line']
        for line in self:
            if line.analytics_id:
                if not line.journal_id.analytic_journal_id:
                    raise exceptions.Warning(
                        _('No Analytic Journal!'),
                        _("You have to define an analytic journal on \
the '%s' journal.") % (line.journal_id.name,))

                toremove = analytic_line_obj.search(
                    [('move_id', '=', line.id)])
                if toremove:
                    toremove.unlink()
                for line2 in line.analytics_id.account_ids:
                    val = (line.credit or 0.0) - (line.debit or 0.0)
                    amt = val * (line2.rate / 100)
                    al_vals = {
                        'name': line.name,
                        'date': line.date,
                        'account_id': line2.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'product_id': line.product_id and
                        line.product_id.id or False,
                        'product_uom_id': line.product_uom_id and
                        line.product_uom_id.id or False,
                        'amount': amt,
                        'general_account_id': line.account_id.id,
                        'move_id': line.id,
                        'journal_id': line.journal_id.analytic_journal_id.id,
                        'ref': line.ref,
                        'percentage': line2.rate,
                        'campaign': line2.campaign.id
                    }
                    analytic_line_obj.create(al_vals)
        return True
