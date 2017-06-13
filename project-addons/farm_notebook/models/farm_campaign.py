# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class FarmCampaign(models.Model):

    _name = 'farm.campaign'

    name = fields.Char(required=True)
    year = fields.Char(required=True)
    notes = fields.Text()
    cultivated_area = fields.Float(compute='_compute_cultivated_area')
    raw_material = fields.Char(required=True)
    raw_material_produced = fields.Float()
    state = fields.Selection(
        (('progress', 'In progress'), ('done', 'Done')), default='progress')
    crops = fields.One2many('farm.crop', 'campaign')

    @api.multi
    @api.depends('crops.cultivated_area')
    def _compute_cultivated_area(self):
        for campaign in self:
            campaign.cultivated_area = sum(
                [x.cultivated_area for x in campaign.crops])

    @api.multi
    def campaign_done(self):
        self.state = 'done'


class FarmCrop(models.Model):

    _name = 'farm.crop'

    campaign = fields.Many2one('farm.campaign', required=True)
    field = fields.Many2one('res.partner.fields', required=True)
    cultivated_area = fields.Float()

    @api.onchange('field')
    def onchange_field(self):
        if self.field:
            self.cultivated_area = self.field.net_surface
