# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductProduct(models.Model):

    _inherit = 'product.product'


    phytosanitary = fields.Boolean()
