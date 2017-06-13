# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResPartnerFields(models.Model):

    _inherit = 'res.partner.fields'

    phytosanitary_uses = fields.One2many('phytosanitary.use', 'partner_field')
    campaigns = fields.One2many('farm.crop', 'field')
    townhall_name = fields.Char()
    aggregate_code = fields.Char()
    sixpac_use = fields.Char()
    irrigation_dry = fields.Selection(
        (('irrigation', 'Irrigation'), ('dry', 'Dry land')),
        'Irrigation / dry land')
    outdoor_protected = fields.Selection(
        (('outdoor', 'Outdoor'), ('protected', 'Protected')),
        'Outdoor / protected')
