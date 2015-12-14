# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, tools, exceptions, _


class mail_attachment_partner(models.Model):

    _name = 'mail.attachment.partner'
    _auto = False

    name = fields.Text('Subject')
    body = fields.Text('Body')
    partner_id = fields.Many2one('res.partner', 'Partner')
    attachment_id = fields.Many2one('ir.attachment', 'Attachment')
    datas = fields.Binary(related='attachment_id.datas')
    datas_fname = fields.Char(related='attachment_id.datas_fname')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE VIEW mail_attachment_partner as (
        select row_number() over () as id, mm.subject as name, mm.body as body, mn.partner_id as partner_id, mar.attachment_id as attachment_id
        from mail_notification mn join message_attachment_rel mar
            on mn.message_id=mar.message_id
        join mail_message mm on mn.message_id=mm.id
        )
""")
