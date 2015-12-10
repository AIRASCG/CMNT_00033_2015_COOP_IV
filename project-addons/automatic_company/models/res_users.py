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
from openerp import models, api
import collections


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.multi
    def add_farms(self):
        for usr in self:
            tot_companies = self.env['res.company']
            for company in usr.company_ids:
                tot_companies += self.env['res.company'].search(
                    [('id', 'child_of', company.id), ('id', 'not in', tot_companies._ids)])
            usr.company_ids = tot_companies
        return True
