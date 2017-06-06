# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ProkectWorkType(models.Model):

    _name = 'project.work.type'

    name = fields.Char(required=True)


class ProjectTaskWork(models.Model):

    _inherit = 'project.task.work'

    def _get_task_date(self):
        return self._context.get('task_date', fields.Date.today())

    work_type = fields.Many2one('project.work.type')
    task_id = fields.Many2one(string='Daily part')
    user_id = fields.Many2one(compute='_compute_user_id')
    exploitation_id = fields.Many2one(
        'res.partner', 'Exploitation',
        domain="[('farm', '=', True),('is_cooperative','=',False)]")
    date_start = fields.Datetime(default=_get_task_date)
    date_end = fields.Datetime(default=_get_task_date)

    @api.depends('task_id.user_id')
    def _compute_user_id(self):
        for work in self:
            work.user_id = work.task_id.user_id

    @api.multi
    def _check_dates(self):
        # Comprobamos que no se solape con otro project.task.work
        # del mismo usuario
        self.ensure_one()
        concurrent_work = self.search(
            ['&', '&', ('id', '!=', self.id),
             ('user_id', '=', self.user_id.id), '|', '|', '&',
             ('date_start', '>=', self.date_start),
             ('date_start', '<=', self.date_end),
             '&', ('date_end', '>=', self.date_start),
             ('date_end', '<=', self.date_end),
             '&', ('date_start', '<=', self.date_start),
             ('date_end', '>=', self.date_start)])
        if concurrent_work:
            raise exceptions.Warning(
                _('Work time error'),
                _('The work time collapses with other works'))

    @api.model
    def create(self, vals):
        res = super(ProjectTaskWork, self).create(vals)
        res._check_dates()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTaskWork, self).write(vals)
        for work in self:
            work._check_dates()
        return res


class ProjectTask(models.Model):

    _inherit = 'project.task'

    name = fields.Date(default=fields.Date.today)
    area = fields.Many2one('project.category')
    km_company_car = fields.Float()
    km_own_car = fields.Float()
    diet = fields.Float()
