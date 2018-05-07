# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class FarmVisitRerport(models.AbstractModel):
    _name = 'report.custom_project.farm_visit_report'

    @api.multi
    def render_html(self, data=None):
        def format_hour(inner):
            if isinstance(inner, str):
                inner = float(inner)
            return '%02d:%02d' % (int(inner), (inner - int(inner)) * 60)
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'custom_project.farm_visit_report')
        all_tasks_dict = data['form']['all_tasks_dict']
        all_users = sorted(data['form']['all_users'])
        table = u'<table class="table table-bordered"><thead><tr><th></th>'
        for user_id in all_users:
            user_name = self.env['res.users'].sudo().browse(user_id).name
            table += u'<th>{}</th>'.format(user_name)
        table += u'</tr></thead><tbody>'
        for work_type_id in all_tasks_dict.keys():
            work_type_name = self.env['project.work.type'].sudo().browse(int(work_type_id)).name
            table += u'<tr><td>{}</td>'.format(work_type_name)
            curr_index = 0
            for user_id in sorted([int(x) for x in all_tasks_dict[work_type_id].keys()]):
                mult = all_users.index(int(user_id))
                mult -= curr_index
                table += u'<td></td>' * mult
                table += u'<td align="right">{}</td>'.format(format_hour(all_tasks_dict[work_type_id][str(user_id)]))
                curr_index += mult + 1
            table += '<td></td>' * (len(all_users) - curr_index)
            table += u'</tr>'
        table += u'</tbody></table>'
        docs = []
        docargs = {
            'doc_ids': data['ids'],
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'tasks': self.env['project.task.work'].browse(data['form']['tasks']),
            'table': table
        }
        return report_obj.sudo().render('custom_project.farm_visit_report',
                                 docargs)
