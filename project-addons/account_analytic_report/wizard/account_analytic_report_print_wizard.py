# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class AccountAnalyticReportPrintWizard(models.TransientModel):

    _name = 'account.analytic.report.print.wizard'

    exploitation = fields.Many2one('res.company', required=True)
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    milk = fields.Float(default=1)
    total_cows = fields.Float(default=1)
    employees = fields.Float(default=1)
    total_heifer = fields.Float(default=1)
    hectare = fields.Float(default=1)
    type = fields.Selection((('xlsx', '.XLSX'), ('pdf', '.PDF')))

    @api.multi
    def print_report(self):
        pyg_1000 = self.env.ref('account_analytic_report.pyg_1000')
        pyg_cow = self.env.ref('account_analytic_report.pyg_cow')
        pyg_employee = self.env.ref('account_analytic_report.pyg_employee')
        pyg_ha = self.env.ref('account_analytic_report.pyg_ha')
        report_vals = {
            'name': '-', 'ref_1': 'res.company,%s' % self.exploitation.id,
            'from_date_1': self.from_date, 'to_date_1': self.to_date,
            'milk_1': self.milk,
            'total_cows_1': self.total_cows,
            'employees_1': self.employees,
            'total_heifer_1': self.total_heifer,
            'hectare_1': self.hectare,
            'template_id': pyg_1000.id,
            'name': 'PYG 4 columnas',
            'active': False
        }
        report_1000 = self.env['account.analytic.report'].create(report_vals)
        report_1000.calculate()

        report_vals.update({'template_id': pyg_cow.id, 'name': 'PYG Vaca 4 col'})
        report_cow = self.env['account.analytic.report'].create(report_vals)
        report_cow.calculate()


        report_vals.update({'name': 'PYG Empleado 4 col', 'template_id': pyg_employee.id})
        report_employee = self.env['account.analytic.report'].create(report_vals)
        report_employee.calculate()


        report_vals.update({'name': 'PYG hectarea 4 col', 'template_id': pyg_ha.id})
        report_ha = self.env['account.analytic.report'].create(report_vals)
        report_ha.calculate()
        datas = {'ids': self._context.get('active_ids', [])}
        res = {'pyg_1000': report_1000.id, 'pyg_cow': report_cow.id,
               'pyg_employee': report_employee.id, 'pyg_ha': report_ha.id}
        datas['form'] = res
        if self.type == 'pdf':
            return self.env['report'].get_action(
                self, 'account_analytic_report.multi_pyg_report', data=datas)
        else:
            datas['form'].update(report_vals)
            datas['form']['exploitation_name'] = self.exploitation.name
            action =  self.env['report'].get_action(
                self, 'multi_pyg_report_aeroo', data=datas)
            action['datas'] = action['data']
            return action

    @api.onchange('exploitation', 'from_date', 'to_date')
    def onchange_exploitation(self):
        if self.exploitation and self.from_date and self.to_date:
            new_obj = self.env['account.analytic.report'].new(
                {'name': '.', 'ref_1': 'res.company,%s' % self.exploitation.id,
                 'from_date_1': self.from_date,
                 'to_date_1': self.to_date})
            new_obj.act_button_update_fields()
            self.milk = new_obj.milk_1 or 1.0
            self.total_cows = new_obj.total_cows_1 or 1.0
            self.employees = new_obj.employees_1 or 1.0
            self.total_heifer = new_obj.total_heifer_1 or 1.0
            self.hectare = new_obj.hectare_1 or 1.0
