# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _


class AccountAnalyticAccountMonthReportWizard(models.TransientModel):

    _name = 'account.analytic.account.month.report.wizard'
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    exploitation= fields.Many2one('res.company', domain=[('parent_id', '!=', False)])

    @api.multi
    def print_report(self):
        self.ensure_one()
        datas = {
            'model': 'account.analytic.account.month.report.wizard',
            'from_date': self.from_date,
            'to_date': self.to_date,
            'company_id': self.exploitation.id,
            'ids': [self.id]
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'analytic.account.month.report.xlsx',
            'datas': datas,
        }
