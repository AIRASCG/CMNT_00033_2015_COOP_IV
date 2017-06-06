# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ui(models.Model):

    _name = 'farm.notebook'

    partner = fields.Many2one('res.partner')
    date = fields.Date()
    phyotsanitary_applicators = fields.Many2many(
        'phytosanitary.applicator')
