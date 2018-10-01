# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api


class MultiPygReportParser(models.AbstractModel):

    _name = 'report.account_analytic_report.multi_pyg_report'

    def _get_value(self, pyg, line):
        converter = self.pool.get(
            'ir.qweb.field.float', self.pool['ir.qweb.field'])
        return converter.value_to_html(
            self.env.cr, self.env.uid,
            pyg.line_ids.filtered(lambda r: r.code == line.code).value_1_2,
            line._fields['value_1_2'], context=self.env.context)

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'account_analytic_report.multi_pyg_report')
        docs = []
        employee_attendance = {}
        totals = {}
        pyg_1000 = self.env['account.analytic.report'].browse(data['form']['pyg_1000'])
        pyg_cow = self.env['account.analytic.report'].browse(data['form']['pyg_cow'])
        pyg_employee = self.env['account.analytic.report'].browse(data['form']['pyg_employee'])
        pyg_ha = self.env['account.analytic.report'].browse(data['form']['pyg_ha'])
        docargs = {
            'doc_ids': data['ids'],
            'doc_model': report.model,
            'docs': docs,
            'pyg_1000': pyg_1000,
            'pyg_cow': pyg_cow,
            'pyg_employee': pyg_employee,
            'pyg_ha': pyg_ha,
            'data': data,
            'get_value': self._get_value
        }
        return report_obj.render('account_analytic_report.multi_pyg_report',
                                 docargs)
