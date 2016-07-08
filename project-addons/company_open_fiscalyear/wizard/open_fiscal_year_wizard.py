# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api
from datetime import date


class CompanyOpenFiscalYear(models.TransientModel):

    _name = 'company.open.fiscal.year'

    def _get_curryear(self):
        return date.today().year

    year = fields.Integer(default=_get_curryear)

    @api.multi
    def open_fiscalyear(self):
        self.ensure_one()
        company = self.env['res.company'].browse(self._context.get('active_id', False))
        company.open_fiscalyear(self.year)
        return {'type': 'ir.actions.act_window_close'}
