# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _


class FarmVisitRerport(models.TransientModel):

    _name = 'print.farm.visit.report'

    user_id = fields.Many2one('res.users')
    farm_id = fields.Many2one(
        'res.partner', 'Exploitation',
        domain="[('farm', '=', True),('is_cooperative','=',False)]")
    date_start = fields.Date()
    date_end = fields.Date()
    work_type = fields.Many2one('project.work.type')


    @api.multi
    def print_report(self):
        domain = []
        if self.farm_id:
            domain.append(
                ('lot_id.farm_id', '=', self.farm_id.id))
        if self.date_start:
            domain.append(('task_id.name', '>=', self.date_start))
        if self.date_end:
            domain.append(('task_id.name', '<=', self.date_end))
        all_users = []
        all_tasks = self.env['project.task.work'].sudo().read_group(
            domain,
            ['work_type', 'user_id', 'hours'], ['work_type', 'user_id'], lazy=True)
        all_tasks_dict = {}
        #import ipdb; ipdb.set_trace()
        for res in all_tasks:
            dict_key = res['work_type'] and res['work_type'][0] or False
            all_tasks_dict[dict_key] = {}
            new_grouped_tasks =  self.env['project.task.work'].\
                sudo().read_group(res['__domain'],
                                  ['user_id', 'hours'],
                                  res['__context']['group_by'], orderby='user_id')
            for res2 in new_grouped_tasks:
                if res2['user_id'][0] not in all_users:
                    all_users.append(res2['user_id'][0])
                all_tasks_dict[dict_key][res2['user_id'][0]] = res2['hours']

        if self.user_id:
            domain.append(('user_id', '=', self.user_id.id))
        if self.work_type:
            domain.append(('work_type', '=', self.work_type.id))
        tasks = self.env['project.task.work'].sudo().search(domain)
        data = self.read()[0]
        data['all_tasks_dict'] = all_tasks_dict
        data['all_users'] = all_users
        data['tasks'] = tasks._ids
        datas = {
            'ids': self._ids,
            'model': 'print.farm.visit.report',
            'form': data,
        }
        return self.env['report'].get_action(self, 'custom_project.farm_visit_report', data=datas)
