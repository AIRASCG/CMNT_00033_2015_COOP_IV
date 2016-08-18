# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        for partner in self:
            if partner in self.env['res.users'].search(
                    []).mapped('partner_id') and vals.get('company_id', False):
                vals['company_id'] = False
        return super(ResPartner, self).write(vals)
