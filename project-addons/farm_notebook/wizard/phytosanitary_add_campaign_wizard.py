# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class PhytosanitaryAddCampaign(models.TransientModel):

    _name = 'phytosanitary.add.campaign'

    campaign = fields.Many2one('farm.campaign', required=True)
    applicator = fields.Many2one('phytosanitary.applicator', required=True)
    machine = fields.Many2one('phytosanitary.machine', required=True)
    date = fields.Date(required=True)

    @api.multi
    def add_campaign(self):
        self.ensure_one()
        uses = []
        for crop in self.campaign.crops:
            uses.append(
                (0, 0,
                 {'campaign': self.campaign.id,
                  'partner_field': crop.field.id,
                  'applicator': self.applicator.id,
                  'machine': self.machine.id, 'date': self.date}))
        self.env['phytosanitary'].browse(
            self._context.get('active_id')).write({'phytosanitary_uses': uses})
        return {'type': 'ir.actions.act_window_close'}
