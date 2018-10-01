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

    def _get_company(self):
        company_setted = self.sudo().env['res.company'].browse(self.env.user.company_id.id)
        return company_setted.cooperative_company

    work_type_ids = fields.One2many('project.work.type', 'categ_id',
                                    'Work types')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_get_company,
                                 domain=[('is_cooperative', '=', True)])

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
    user_id = fields.Many2one(compute='_compute_user_id', store=True)
    exploitation_id = fields.Many2one(
        'res.partner', 'Exploitation',
        domain="[('farm', '=', True),('is_cooperative','=',False)]")
    date_start = fields.Float()
    date_end = fields.Float()
    absence = fields.Boolean()
    absence_type = fields.Many2one('absence.type')
    lot_id = fields.Many2one('lot', 'Lot')
    area = fields.Many2one('project.category', related='task_id.area', readonly=True)
    name = fields.Text()

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

    @api.onchange('task_id')
    def onchange_task_id(self):
        for task_work in self:
            task_work.date = task_work.task_id.name

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
        res.date = res.task_id.name
        res._check_dates()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTaskWork, self).write(vals)
        if not self._context.get('checked_on_task', False):
            for work in self:
                work._check_dates()
        return res


class ProjectTask(models.Model):

    _inherit = 'project.task'
    _order = "name desc"

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
    reviewer_2_id = fields.Many2one('res.users', 'Reviewer 2', select=True, track_visibility='onchange')

    @api.model
    def _message_get_auto_subscribe_fields(self, updated_fields,
                                           auto_follow_fields=None):
        if auto_follow_fields is None:
            auto_follow_fields = ['user_id', 'reviewer_id', 'reviewer_2_id']
        else:
            auto_follow_fields.append('reviewer_2_id')
        return super(ProjectTask, self)._message_get_auto_subscribe_fields(
            updated_fields, auto_follow_fields)

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
            user = self.env['res.users'].browse(user_id)
            res['value']['reviewer_id'] = user.reviewer_id.id
            res['value']['reviewer_2_id'] = user.reviewer_2_id.id
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self.with_context(checked_on_task=True)).write(vals)
        for work in self.work_ids:
            work._check_dates()
        return res
