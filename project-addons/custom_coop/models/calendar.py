# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    def _get_categ_ids(self):
        categs = self.env['calendar.event.type']
        for group in self.env.user.groups_id:
            if group.default_event_categories:
                categs += group.default_event_categories
        return categs

    categ_ids = fields.Many2many(default=_get_categ_ids)
