# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from openerp import models, fields, api, exceptions, _


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(ProductProduct, self).\
            fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                            context=context, toolbar=toolbar, submenu=submenu)
        no_create = context.get('no_create', False)
        update = (no_create and view_type in ['form', 'tree']) or False
        if update:
            doc = etree.XML(res['arch'])
            if no_create:
                for t in doc.xpath("//"+view_type):
                    t.attrib['create'] = 'false'
            res['arch'] = etree.tostring(doc)
        no_unlink = context.get('no_unlink', False)
        update = (no_unlink and view_type in ['form', 'tree']) or False
        if update:
            doc = etree.XML(res['arch'])
            if no_unlink:
                for t in doc.xpath("//"+view_type):
                    t.attrib['delete'] = 'false'
            res['arch'] = etree.tostring(doc)

        return res
