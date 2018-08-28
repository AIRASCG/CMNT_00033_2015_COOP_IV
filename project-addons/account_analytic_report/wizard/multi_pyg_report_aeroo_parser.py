# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):
    """Parser"""
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_value': self._get_value,
            'lang': 'es_ES'
        })

    def _get_value(self, report, value, total=False):
        report_name = 'pyg_%s' % report
        obj = self.localcontext.get(report_name)
        if not obj:
            obj = self.pool.get('account.analytic.report').browse(
                self.cr, self.uid,
                self.localcontext['data']['form'][report_name])
            self.localcontext[report_name] = obj
        if isinstance(value, int):
            value = str(value)
        if value == 'title':
            if total:
                return obj.title_1
            return obj.title_2
        else:
            column = 'value_1_2'
            if total:
                column = 'value_1_1'
            return obj.line_ids.filtered(lambda r: r.code == value)[column]
