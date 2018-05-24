# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class FarmCampaignAddFarms(models.TransientModel):

    _name = 'farm.campaign.add.fields'

    fields_add = fields.Many2many('res.partner.fields')
    not_show_fields = fields.Many2many(
        'res.partner.fields',
        'farm_campaing_add_fields_field_rel2',
        compute='_compute_not_show_fields')

    @api.depends('fields_add')
    def _compute_not_show_fields(self):
        self.not_show_fields = self.env['farm.campaign'].browse(
            self._context.get('active_id', False)).mapped('crops.field')

    @api.multi
    def confirm(self):
        crops = []
        campaign = self.env['farm.campaign'].browse(
            self._context.get('active_id', False))
        for field in self.fields_add:
            crops.append(
                (0, 0,
                 {'campaign': self._context.get('active_id'),
                  'field': field.id,
                  'cultivated_area': field.net_surface}))
        campaign.write({'crops': crops})
        return {'type': 'ir.actions.act_window_close'}
