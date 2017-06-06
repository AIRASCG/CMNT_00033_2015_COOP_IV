# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class Phytosanitary(models.Model):

    _name = 'phytosanitary'

    def _get_company(self):
        return self.env.user.company_id

    invoice_line = fields.Many2one('account.invoice.line')
    total_qty = fields.Float(required=True)
    uom = fields.Many2one('product.uom', required=True)
    registry_number = fields.Char(required=True)
    name = fields.Char(required=True)
    acquisition_date = fields.Date(required=True)
    phytosanitary_uses = fields.One2many('phytosanitary.use', 'phytosanitary')
    rest_qty = fields.Float(compute='_compute_rest_qty', store=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company)

    @api.depends('total_qty', 'phytosanitary_uses.used_qty')
    def _compute_rest_qty(self):
        for phyto in self:
            phyto.rest_qty = phyto.total_qty - \
                sum([x.used_qty for x in phyto.phytosanitary_uses])

    @api.multi
    def name_get(self):
        res = []
        for phyto in self:
            acquisition_date = fields.Date.from_string(phyto.acquisition_date)
            date_format = self.env['res.lang'].search(
                [('code', '=', self.env.user.lang)]).date_format

            acquisition_date_str = acquisition_date.strftime(date_format)
            res.append(
                (phyto.id,
                 '%s %s (%s %s)' %
                 (phyto.name, acquisition_date_str, phyto.rest_qty,
                  phyto.uom.name)))
        return res


class PhytosanitaryUse(models.Model):

    _name = 'phytosanitary.use'

    phytosanitary = fields.Many2one('phytosanitary')
    partner_field = fields.Many2one('res.partner.fields')
    used_qty = fields.Float()
    applicator = fields.Many2one('phytosanitary.applicator', required=True)
    machine = fields.Many2one('phytosanitary.machine', required=True)
    notes = fields.Char()

    @api.model
    def create(self, vals):
        res = super(PhytosanitaryUse, self).create(vals)
        if res.phytosanitary.rest_qty - self.used_qty < 0:
            raise exceptions.Warning(
                _('Qty error'), _('Cantidad disponible insuficiente'))
        return res


class PhytosanitaryMachine(models.Model):

    _name = 'phytosanitary.machine'

    def _get_company(self):
        return self.env.user.company_id.cooperative_company

    name = fields.Char(required=True)
    ROMA_inscription_number = fields.Char()
    acquisition_year = fields.Char()
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company)


class PhytosanitaryApplicator(models.Model):

    _name = 'phytosanitary.applicator'

    def _get_company(self):
        return self.env.user.company_id.cooperative_company

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company)
