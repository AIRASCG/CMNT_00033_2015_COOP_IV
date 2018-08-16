# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse


class Parser(report_sxw.rml_parse):
    """Parser"""
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr,uid,name,context)
        self.localcontext.update({
            'get_field': self._get_field,
            'get_records': self._get_records,
            })

    def _get_field(self, field_name):
        obj = self.pool.get('milk.control.report').browse(self.cr, self.uid, self.localcontext['data']['form']['obj'])
        return obj[field_name + '_' + self.localcontext['data']['form']['exploitation']]

    def _get_records(self):
        obj = self.pool.get('milk.control.report').browse(self.cr, self.uid, self.localcontext['data']['form']['obj'])
        suffix = self.localcontext['data']['form']['exploitation']
        milk_control = self.pool.get('milk.control').search(
            self.cr, self.uid,
            [('date', '>=', obj['from_date_%s' % suffix]),
             ('date', '<=', obj['to_date_%s' % suffix]),
             ('exploitation_id', '=', obj['exploitation_%s' % suffix].id)])
        return self.pool.get('milk.control').browse(self.cr, self.uid, milk_control).mapped('line_ids')
