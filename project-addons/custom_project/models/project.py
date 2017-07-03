# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta


class ProjectProject(models.Model):

    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        return super(ProjectProject, self.with_context(bypass_cud_protection=True)).create(vals)


class ProjectCategory(models.Model):

    _inherit = 'project.category'
    work_type_ids = fields.One2many('project.work.type', 'categ_id',
                                    'Work types')

class AbsenceType(models.Model):

    _name = 'absence.type'
    name = fields.Char()


class ProkectWorkType(models.Model):

    _name = 'project.work.type'

    name = fields.Char(required=True)
    categ_id = fields.Many2one('project.category', 'Area')


class ProjectTaskWork(models.Model):

    _inherit = 'project.task.work'

    work_type = fields.Many2one('project.work.type')
    task_id = fields.Many2one(string='Daily part')
    user_id = fields.Many2one(compute='_compute_user_id')
    exploitation_id = fields.Many2one(
        'res.partner', 'Exploitation',
        domain="[('farm', '=', True),('is_cooperative','=',False)]")
    date_start = fields.Float()
    date_end = fields.Float()
    absence = fields.Boolean()
    absence_type = fields.Many2one('absence.type')
    area = fields.Many2one('project.category', related='task_id.area', readonly=True)

    @api.onchange('date_start', 'date_end')
    def onchange_date_end(self):
        if self.date_start and self.date_end:
            self.hours = self.date_end - self.date_start

    @api.onchange('hours')
    def onchange_hours(self):
        if self.hours and self.date_start:
            self.date_end = self.date_start + self.hours

    @api.depends('task_id.user_id')
    def _compute_user_id(self):
        for work in self:
            work.user_id = work.task_id.user_id

    @api.multi
    def _check_dates(self):
        # Comprobamos que no se solape con otro project.task.work
        # del mismo usuario
        self.ensure_one()
        concurrent_work = self.task_id.work_ids.filtered(
            lambda r: (r.date_start > self.date_start and
                       r.date_start < self.date_end) or
                      (r.date_end > self.date_start and
                       r.date_end < self.date_end) or
                      (r.date_start < self.date_start and
                       r.date_end > self.date_start))
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
    contract_type = fields.Many2one('contract.type',
                                    related='user_id.contract_type',
                                    readonly=True)
    total_work_hours = fields.Float(compute='_compute_total_hours', store=True)
    total_absence_hours = fields.Float(compute='_compute_total_hours',
                                       store=True)
    total_time = fields.Float(compute='_compute_total_hours', store=True)
    notes = fields.Char()

    @api.depends('work_ids.hours', 'work_ids.absence', 'contract_type.hours')
    def _compute_total_hours(self):
        for task in self:
            task.total_work_hours = sum(task.work_ids.filtered(
                lambda r: not r.absence).mapped('hours'))
            task.total_absence_hours = sum(task.work_ids.filtered(
                'absence').mapped('hours'))
            task.total_time = task.total_work_hours - task.contract_type.hours

    @api.multi
    def onchange_user_id(self, user_id):
        res = super(ProjectTask, self).onchange_user_id(user_id)
        if user_id:
            res['value']['reviewer_id'] = self.env['res.users'].browse(
                user_id).reviewer_id.id
        return res
