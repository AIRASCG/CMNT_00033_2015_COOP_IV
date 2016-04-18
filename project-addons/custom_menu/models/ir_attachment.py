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
from openerp import models, fields, api, exceptions, _


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('apply_multicompany'):
            args = args + ['|', ('company_id', 'child_of', [self.env.user.company_id.id]),
                           ('company_id', '=', False)]
            self.env.cr.execute('SELECT attachment_id from mail_attachment_partner')
            res = self.env.cr.fetchall()
            args.append(('id', 'not in', [x[0] for x in res]))
        return super(IrAttachment, self).search(args, offset=offset, limit=limit,
                                                order=order, count=count)
