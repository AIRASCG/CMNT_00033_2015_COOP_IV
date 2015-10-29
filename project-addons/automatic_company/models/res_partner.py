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


class ResPartner(models.Model):

    _inherit = 'res.partner'


    def _get_coop_company_id(self, company_id):
        company_setted = self.env['res.company'].browse(company_id)
        coop_company = company_setted.cooperative_company
        return coop_company.id

    @api.model
    def create(self, vals):
        if vals.get('company_id', False):
            vals['company_id'] = self._get_coop_company_id(vals['company_id'])
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('company_id', False):
            vals['company_id'] = self._get_coop_company_id(vals['company_id'])
        return super(ResPartner, self).write(vals)
