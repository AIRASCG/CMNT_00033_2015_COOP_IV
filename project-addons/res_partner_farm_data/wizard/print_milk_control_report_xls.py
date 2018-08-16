# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _


class PrintMilkControlReportXlsWizard(models.TransientModel):

    _name = 'print.milk.control.report.xls.wizard'

    selected_exploitation = fields.Selection(
        (('1', 'Exploitation 1'), ('2', 'Exploitation 2')), default='1')

    @api.multi
    def print_report(self):
        self.ensure_one()
        report = self.env['milk.control.report'].browse(self._context.get('active_id'))
        type_dict = {
            'total': '0',
            'morning': '1',
            'late': '2',
        }
        datas = {
             'ids': self._context.get('active_ids',[]),
             'model': 'print.milk.control.report.xls.wizard',
             'form': {
                'exploitation': self.selected_exploitation,
                'type': type_dict[report['milking_type_%s' % self.selected_exploitation]],
                'obj': report.id,
             }
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'milk_control_report',
            'datas': datas,
        }
