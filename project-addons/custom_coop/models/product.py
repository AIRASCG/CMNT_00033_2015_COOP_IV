# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ProductProduct(models.Model):

    _inherit = 'product.product'

    _sql_constraints = [
        ('ref_uniq', 'unique (default_code)',
         _('Error! Product reference must be unique.'))
    ]
