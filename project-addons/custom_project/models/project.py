# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ProjectTaskWork(models.Model):

    _inherit = 'project.task.work'

    category_id = fields.Many2one('project.category', 'Tag')
    task_id = fields.Many2one(string='Daily part')
    exploitation_id = fields.Many2one(
        'res.partner', 'Exploitation',
        domain="[('farm', '=', True),('is_cooperative','=',False)]")


class ProjectTask(models.Model):

    _inherit = 'project.task'

    @api.model
    def _get_default_name(self):
        return fields.Date.from_string(fields.Date.today()).strftime('%Y%m%d')

    name = fields.Char(default=_get_default_name)
