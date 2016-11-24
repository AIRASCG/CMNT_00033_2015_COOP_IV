# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from openerp.tools import html_escape as escape
from openerp.addons.base.ir.ir_qweb import HTMLSafe


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    def record_to_html(self, cr, uid, field_name, record, options=None, context=None):
        if context is None:
            context = {}

        if options is None:
            options = {}
        opf = options.get('fields') or ["name", "address", "phone", "mobile", "fax", "email"]

        value_rec = record[field_name]
        if not value_rec:
            return None
        value_rec = value_rec.sudo().with_context(show_address=True)
        value = value_rec.name_get()[0][1]

        val = {
            'name': value.split("\n")[0],
            'address': escape(" ".join(value.split("\n")[1:])),
            'phone': value_rec.phone,
            'mobile': value_rec.mobile,
            'fax': value_rec.fax,
            'city': value_rec.city,
            'country_id': value_rec.country_id.display_name,
            'website': value_rec.website,
            'email': value_rec.email,
            'vat': value_rec.vat,
            'fields': opf,
            'object': value_rec,
            'options': options
        }
        val['address'] = val['address'].replace(val['country_id'], '')
        html = self.pool["ir.ui.view"].render(cr, uid, "base.contact", val, engine='ir.qweb', context=context).decode('utf8')

        return HTMLSafe(html)
