# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class QwebWidgetTime(models.AbstractModel):
    _name = 'ir.qweb.widget.time'
    _inherit = 'ir.qweb.widget'

    def _format(self, inner, options, qwebcontext):
        inner = self.pool['ir.qweb'].eval(inner, qwebcontext)
        if isinstance(inner, str):
            inner = float(inner)
        return '%02d:%02d' % (int(inner), (inner - int(inner)) * 60)
