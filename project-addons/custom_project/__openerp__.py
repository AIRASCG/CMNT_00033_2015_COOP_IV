# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Project customizations',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'project',
        'automatic_company'
    ],
    'data': [
        'views/project.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'report/report_task_daily.xml',
        'report/report_task_hours_summary.xml',
        'report/farm_visit_report.xml',
        'wizard/print_hours_resume.xml',
        'wizard/print_farm_visit_report.xml'
    ],
}
