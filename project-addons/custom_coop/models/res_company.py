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


class ResCompany(models.Model):

    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        if not vals.get('parent_id', False):
            if self.env.user.id != 1:
                raise exceptions.Warning(_('Create error'), _('Parent required'))
        return super(ResCompany, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'parent_id' in vals.keys() and not vals.get('parent_id'):
            if self.env.user.id != 1:
                raise exceptions.Warning(_('Create error'), _('Parent required'))
        return super(ResCompany, self).write(vals)
