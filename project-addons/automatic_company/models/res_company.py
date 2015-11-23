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

    is_cooperative = fields.Boolean('Is a cooperative?')
    cooperative_company = fields.Many2one('res.company', 'Cooperative company',
                                          compute='_get_cooperative_company')

    @api.one
    def _get_cooperative_company(self):
        if self.is_cooperative or not self.sudo().parent_id.is_cooperative:
            self.cooperative_company = self
        else:
            self.cooperative_company = self.sudo().parent_id
