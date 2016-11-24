# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.model
    def change_current_company_to_coop(self):
        use_company = curr_company = self.env.user.company_id
        while use_company.parent_id and not \
                use_company.is_cooperative:
            use_company = use_company.parent_id
        if use_company in self.env.user.company_ids:
            self.env.user.write({'company_id': use_company.id})
