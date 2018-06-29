# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from openerp import models, fields, api, exceptions, _


class PrintHoursResume(models.TransientModel):

    _name = 'print.hours.resume'

    group = fields.Selection(
        (('day', 'Hours / day'), ('month', 'Hours / month')), required=True)
    user_id = fields.Many2one('res.users')
    reviewer_id = fields.Many2one('res.users')
    area = fields.Many2one('project.category')
    date_start = fields.Date()
    date_end = fields.Date()


    @api.multi
    def print_report(self):
        domain = []
        if self.user_id:
            domain.append(('user_id', '=', self.user_id.id))
        if self.area:
            domain.append(('area', '=', self.area.id))
        if self.reviewer_id:
            domain.extend(
                ['|', ('reviewer_id', '=', self.reviewer_id.id),
                 ('reviewer_2_id', '=', self.reviewer_id.id)])
        if self.date_start:
            domain.append(('name', '>=', self.date_start))
        if self.date_end:
            domain.append(('name', '<=', self.date_end))

        tasks = self.env['project.task'].read_group(
            domain,
            ['total_work_hours', 'total_absence_hours', 'total_time',
             'km_company_car', 'km_own_car', 'diet', 'name'],
            'name:{}'.format(self.group))
        data = self.read()[0]
        for task in tasks:
            if self.group == 'day':
                task_date = datetime.strptime(task['name:day'], '%d %b %Y')
                task['show_name'] = task_date.strftime('%a, %d %b %Y')
            else:
                task['show_name'] = task['name:month']
        data['tasks'] = tasks
        datas = {
            'ids': self._ids,
            'model': 'print.hours.resume',
            'form': data,
        }
        return self.env['report'].get_action(self, 'custom_project.task_hours_summary_report', data=datas)
