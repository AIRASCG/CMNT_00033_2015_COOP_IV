# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, tools


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    def _get_categ_ids(self):
        categs = self.env['calendar.event.type']
        for group in self.env.user.groups_id:
            if group.default_event_categories:
                categs += group.default_event_categories
        return categs

    categ_ids = fields.Many2many(default=_get_categ_ids)


class CalendarAttendee(models.Model):

    _inherit = 'calendar.attendee'

    @api.multi
    def _send_mail_to_attendees(
            self, email_from=tools.config.get('email_from', False),
            template_xmlid='calendar_template_meeting_invitation',
            force=False):
        send_attendee = self
        for attendee in self:
            if self.env.ref('custom_groups.group_rancher') in \
                    attendee.partner_id.mapped('user_ids.groups_id'):
                send_attendee -= attendee
        return super(CalendarAttendee, send_attendee)._send_mail_to_attendees(
            email_from, template_xmlid, force)
