# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ResPartnerFields(models.Model):

    _inherit = 'res.partner.fields'

    phytosanitary_uses = fields.One2many('phytosanitary.use', 'partner_field')
    campaigns = fields.One2many('farm.crop', 'field')
