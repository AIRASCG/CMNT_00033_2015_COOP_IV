# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp
import openerp.http as http
from openerp.http import request


class WebEasySwitchCompanyController(http.Controller):
    @http.route(
        '/web_easy_switch_company/switch/change_current_company_coop',
        type='json', auth='none')
    def change_current_company_to_coop(self):
        registry = openerp.modules.registry.RegistryManager.get(
            request.session.db)
        uid = request.session.uid
        with registry.cursor() as cr:
            res = registry.get("res.users").change_current_company_to_coop(
                cr, uid)
            return res
