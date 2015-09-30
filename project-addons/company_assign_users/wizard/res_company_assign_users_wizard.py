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


class ResCompanyAssignUsersWizard(models.TransientModel):

    _name = 'res.company.assign.users.wizard'

    company_id = fields.Many2one('res.company', 'Company',
                                 compute='_get_company_id')
    user_ids = fields.Many2many('res.users',
                                'company_assign_users_wizard_res_user_rel',
                                'wizard_id', 'user_id', 'Users')

    @api.one
    def _get_company_id(self):
        self.company_id = self._context.get('active_id', False)

    @api.multi
    def assign(self):
        self.company_id.write({'user_ids': [(4, x.id) for x in self.user_ids]})
        return {'type': 'ir.actions.act_window_close'}
