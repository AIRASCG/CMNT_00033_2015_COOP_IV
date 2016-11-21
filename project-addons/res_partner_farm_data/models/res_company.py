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
from openerp import models, fields, api, _


class ResCompany(models.Model):

    _inherit = 'res.company'

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         _('A company with the same name already exists'))
    ]

    xml_route = fields.Char()

    @api.one
    def _get_not_configured_accounting(self):
        accounts = self.env['account.account'].search(
            [('company_id', '=', self.id)])
        if self.is_cooperative:
            self.not_configured_accounting = False
        else:
            self.not_configured_accounting = not accounts and True or False

    @api.model
    def create(self, vals):
        company = super(ResCompany,
                        self.with_context(company_partner=True)).create(vals)
        self.sudo().env["res.users"].browse(1).write({'company_ids':
                                                      [(4, company.id)]})
        return company
