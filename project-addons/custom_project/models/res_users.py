# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ContractType(models.Model):

    _name = 'contract.type'

    name = fields.Char()
    hours = fields.Float()


class ResUsers(models.Model):

    _inherit = 'res.users'


    reviewer_id = fields.Many2one('res.users', 'Reviewer')
    reviewer_2_id = fields.Many2one('res.users', 'Reviewer 2')
    is_reviewer = fields.Boolean()
    contract_type = fields.Many2one('contract.type', 'Contract type')
