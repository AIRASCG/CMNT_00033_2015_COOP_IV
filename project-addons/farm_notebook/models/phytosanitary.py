# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class PhytosanitaryRegistryNumber(models.Model):

    _name = 'phytosanitary.registry.number'

    name = fields.Char("Nº registro", required=True)
    commercial_name = fields.Char("Nombre comercial")
    company_name = fields.Char("Titular")
    formula = fields.Char("Formulado")

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        domain = ['|', ('commercial_name', operator, name),
                  ('name', operator, name)]
        ids = self.search(cr, user, domain + args, limit=limit,
                          context=context)
        return self.name_get(cr, user, ids, context=context)

    @api.multi
    def name_get(self):
        result = []
        for reg in self:
            result.append((reg.id, "%s %s" %
                           (reg.name, reg.commercial_name or '')))
        return result


class Phytosanitary(models.Model):

    _name = 'phytosanitary'
    _order = "acquisition_date desc"

    def _get_company(self):
        return self.env.user.company_id

    invoice_line = fields.Many2one('account.invoice.line')
    total_qty = fields.Float(required=True)
    uom = fields.Many2one('product.uom', required=True)
    registry_number = fields.Many2one('phytosanitary.registry.number',
                                      required=True)
    name = fields.Char(required=True)
    acquisition_date = fields.Date(required=True)
    phytosanitary_uses = fields.One2many('phytosanitary.use', 'phytosanitary')
    rest_qty = fields.Float(compute='_compute_rest_qty', store=True,
                            digits=(13, 4))
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

    phytosanitary = fields.Many2one('phytosanitary', required=True,
                                    ondelete='cascade')
    date = fields.Date()
    partner_field = fields.Many2one('res.partner.fields', required=False,
                                    ondelete='cascade')
    campaign = fields.Many2one('farm.campaign', required=True,
                               ondelete='cascade')
    surface_treated = fields.Float()
    phytosanitary_problem = fields.Char()
    efficacy = fields.Char()
    used_qty = fields.Float(compute='_compute_used_qty', store=True,
                            digits=(13, 4))
    used_doses = fields.Float("Dosis/Hm")
    applicator = fields.Many2one('phytosanitary.applicator')
    machine = fields.Many2one('phytosanitary.machine')
    notes = fields.Char()
    year = fields.Char(compute='_compute_use_year')

    @api.depends('used_doses', 'surface_treated')
    def _compute_used_qty(self):
        for use in self:
            use.used_qty = use.used_doses * use.surface_treated

    @api.depends('date')
    def _compute_use_year(self):
        for use in self:
            if use.date:
                use.year = use.date[:4]

    @api.onchange('partner_field')
    def onchange_partner_field(self):
        if self.partner_field:
            self.surface_treated = self.partner_field.net_surface
            return {'domain': {'campaign':
                    [('id', 'in',
                      self.mapped('partner_field.campaigns.campaign.id'))]}}

    @api.onchange('campaign')
    def onchange_campaign(self):
        if self.campaign:
            crops = self.campaign.crops.filtered(
                lambda r: r.field == self.partner_field)
            if len(crops) > 1:
                self.surface_treated = sum(crops.mapped('cultivated_area'))
            else:
                self.surface_treated = crops.cultivated_area


class PhytosanitaryMachine(models.Model):

    _name = 'phytosanitary.machine'

    def _get_company(self):
        return self.env.user.company_id.cooperative_company

    name = fields.Char(required=True)
    ROMA_inscription_number = fields.Char()
    acquisition_year = fields.Char()
    inspection_date = fields.Date()
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company)


class PhytosanitaryApplicator(models.Model):

    _name = 'phytosanitary.applicator'

    def _get_company(self):
        return self.env.user.company_id.cooperative_company

    name = fields.Char(required=True)
    vat = fields.Char()
    ropo = fields.Char('ROPO number')
    license_type = fields.Selection(
        (('basic', 'Basic'), ('qualified', 'Qualified'),
         ('fumigation', 'Fumigation'), ('pilot', 'pilot')))
    adviser = fields.Char()
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company)
