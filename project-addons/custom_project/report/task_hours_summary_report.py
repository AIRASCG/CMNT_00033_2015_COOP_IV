# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from datetime import datetime, date
import time
import locale
import os
from openerp import models, fields, api, exceptions, _


class TaskHoursSummaryReport(models.AbstractModel):
    _name = 'report.custom_project.task_hours_summary_report'

    @api.multi
    def _make_graphic(self, datas, group):
        ax = plt.axes()
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")
        if group == 'day':
            date_format = '%d %b %Y'
        else:
            loc = mdates.MonthLocator()
            date_format = '%B %Y'
        dates = [datetime.strptime(x['name:{}'.format(group)], date_format) for x in datas]
        hours = [x['total_work_hours'] for x in datas]
        if not dates:
            return
        if group == 'day':
            diff = abs((dates[0] - dates[-1]).days)
            if diff < 30:
                loc = mdates.DayLocator()
            elif diff > 30 and diff < 100:
                loc = mdates.WeekdayLocator()
            else:
                loc = mdates.MonthLocator()

        fmt = mdates.DateFormatter(date_format)
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(fmt)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda inner, _: '%02d:%02d' % (int(inner), (inner - int(inner)) * 60)))
        plt.bar(dates, hours, align="center", color='green')
        plt.title(_('total worked hours / ') + _(group))
        plt.grid(True)
        fig = plt.figure(1)
        fig.autofmt_xdate()
        filename = '/tmp/{}_{}.png'.format(time.mktime(datetime.now().timetuple()), self.id)
        plt.savefig(filename)
        with open(filename, 'rb') as image_file:
            image_b64 = base64.b64encode(image_file.read())
        os.remove(filename)
        plt.close()
        return image_b64

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'custom_project.task_hours_summary_report')
        docs = []
        docargs = {
            'doc_ids': data['ids'],
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'graphic': self._make_graphic(data['form']['tasks'], data['form']['group']),
            'tasks': data['form']['tasks']
        }
        return report_obj.render('custom_project.task_hours_summary_report',
                                 docargs)
