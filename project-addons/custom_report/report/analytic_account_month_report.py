# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import calendar
from datetime import datetime, timedelta, date


class AnalyticAccountMonthReportXlsx(ReportXlsx):

    def get_employee_qty(self, env, partner, from_date, to_date):
        employee_count = env['employee.farm.count'].search(
            [('partner_id', '=', partner.id),
             ('date', '>=', from_date),
             ('date', '<=', to_date)], order="date asc")
        last_employee =  self.env['employee.farm.count'].search(
            [('partner_id', '=', partner.id),
             ('date', '<', from_date)], order="date desc",
            limit=1)
        if not employee_count and not last_employee:
            return 0.0
        if employee_count:
            sorted(employee_count, key=lambda x: x.date)
        indice = 0
        first_date = datetime.strptime(from_date, '%Y-%m-%d')

        if employee_count:
            second_date = datetime.strptime(employee_count[0].date,
                                            '%Y-%m-%d')
        else:
            second_date = datetime.strptime(to_date, '%Y-%m-%d')
        sum_days = (second_date - first_date).days
        employees = (last_employee and last_employee.quantity or 0) * sum_days
        first_date = second_date
        total_count = employee_count and len(employee_count) or 0
        for j in range(total_count):
            if indice+1 < total_count:
                second_date = datetime.strptime(employee_count[indice+1].date, '%Y-%m-%d')
            else:
                second_date = datetime.strptime(to_date, '%Y-%m-%d')
            dif_dates = second_date - first_date
            employees += employee_count[j].quantity * dif_dates.days
            first_date = second_date
            sum_days += dif_dates.days
            indice += 1
        if sum_days > 0:
            return float(employees) / sum_days

    def get_milk(self, env, partner, from_date, to_date):
        quotas = self.env['output.quota'].search(
            [('farm_id', '=', partner.id),
             ('date', '>=', from_date),
             ('date', '<=', to_date)])
        return sum([x.value for x in quotas])

    def _add_account(self, env, company, account, periods):
        self.sheet.write_string(self.current_row, 0, account.code or '')
        self.sheet.write_string(self.current_row, 1, account.name or '')
        curr_column = 2
        quantity_sum = 0
        balance_sum = 0
        for period in periods:
            account_ctx =  account.with_context(from_date=period[0], to_date=period[1], company_id=company.id)
            balance = account_ctx.balance
            quantity = account_ctx.quantity
            quantity_sum += quantity
            balance_sum += balance
            self.sheet.write_number(self.current_row, curr_column, quantity)
            self.sheet.write_number(self.current_row, curr_column + 1, balance)
            curr_column += 2
        self.sheet.write_number(self.current_row, curr_column, quantity_sum)
        self.sheet.write_number(self.current_row, curr_column + 1, balance_sum)
        self.current_row += 1
        for child in account.child_ids:
            self._add_account(env, company, child, periods)

    def get_total_cows(self, env, partner, from_date, to_date):
        cow_counts = self.env['cow.count'].search(
            [('partner_id', '=', partner.id),
             ('date', '>=', from_date),
             ('date', '<=', to_date)], order="date asc")
        last_cow = self.env['cow.count'].search(
            [('partner_id', '=', partner.id),
             ('date', '<', from_date)], order="date desc",
            limit=1)
        if not cow_counts and not last_cow:
            return 0.0
        if cow_counts:
            sorted(cow_counts, key=lambda x: x.date)

        total_count = cow_counts and len(cow_counts) or 0
        indice = 0
        first_date = datetime.strptime(from_date, '%Y-%m-%d')

        if cow_counts:
            second_date = datetime.strptime(cow_counts[0].date, '%Y-%m-%d')
        else:
            second_date = datetime.strptime(to_date, '%Y-%m-%d')
        sum_days = (second_date - first_date).days
        heifer_0_3 = (last_cow and last_cow.heifer_0_3 or 0) * sum_days
        heifer_3_12 = (last_cow and last_cow.heifer_3_12 or 0) * sum_days
        heifer_plus_12 = (last_cow and last_cow.heifer_plus_12 or 0) * sum_days
        milk_cow = (last_cow and last_cow.milk_cow or 0) * sum_days
        dry_cow = (last_cow and last_cow.dry_cow or 0) * sum_days

        first_date = second_date
        for j in range(total_count):
            if indice+1 < total_count:
                second_date = datetime.strptime(cow_counts[indice+1].date, '%Y-%m-%d')
            else:
                second_date = datetime.strptime(to_date, '%Y-%m-%d')
            dif_dates = second_date - first_date
            heifer_0_3 += cow_counts[j].heifer_0_3 * dif_dates.days
            heifer_3_12 += cow_counts[j].heifer_3_12 * dif_dates.days
            heifer_plus_12 += cow_counts[j].heifer_plus_12 * dif_dates.days
            dry_cow += cow_counts[j].dry_cow * dif_dates.days
            milk_cow += cow_counts[j].milk_cow * dif_dates.days
            first_date = second_date
            sum_days += dif_dates.days
            indice += 1
        if sum_days > 0:
            heifer_0_3 = float(heifer_0_3) / sum_days
            heifer_3_12 = float(heifer_3_12) / sum_days
            heifer_plus_12 = float(heifer_plus_12) / sum_days
            milk_cow = float(milk_cow) / sum_days
            dry_cow = float(dry_cow) / sum_days

        total_cows = round(sum((milk_cow, dry_cow)), 2)
        total_heifer = sum((heifer_0_3, heifer_3_12, heifer_plus_12))

        return total_cows, total_heifer

    def generate_xlsx_report(self, workbook, data, objects):
        self.sheet = workbook.add_worksheet()
        company = objects.env['res.company'].browse(data['company_id'])
        from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
        periods = []
        while from_date < to_date:
            last_period_date = date(
                from_date.year,
                from_date.month,
                calendar.monthrange(from_date.year, from_date.month)[1])
            if last_period_date > to_date:
                last_period_date = to_date
            periods.append((from_date, last_period_date))
            from_date = last_period_date + + timedelta(days=1)
        self.sheet.write_string(0, 0, 'Leche')
        self.sheet.write_string(0, 1, 'Total vacas')
        self.sheet.write_string(0, 2, 'Empleados')
        self.sheet.write_string(0, 3, 'Total novillas')
        total_cows, total_heifer = self.get_total_cows(objects.env, company.partner_id, data['from_date'], data['to_date'])
        self.sheet.write_number(1, 0, self.get_milk(objects.env, company.partner_id, data['from_date'], data['to_date']))
        self.sheet.write_number(1, 1, total_cows)
        self.sheet.write_number(1, 2, self.get_employee_qty(objects.env, company.partner_id, data['from_date'], data['to_date']))
        self.sheet.write_number(1, 3, total_heifer)
        curr_column = 2
        for period in periods:
            self.sheet.merge_range(5, curr_column, 5, curr_column + 1, '{} - {}'.format(period[0].month, period[0].year))
            self.sheet.write_string(6, curr_column, 'UD')
            self.sheet.write_string(6, curr_column + 1, u'€')
            curr_column += 2
        self.sheet.merge_range(5, curr_column, 5, curr_column + 1, 'SUMA')
        self.sheet.write_string(6, curr_column, 'UD')
        self.sheet.write_string(6, curr_column + 1, u'€')
        self.sheet.write_string(7, 0, u'Cuenta analítica')
        self.sheet.write_string(7, 1, u'Nombre')
        self.current_row = 8
        for account in objects.env['account.analytic.account'].search([('parent_id', '=', False)]):
            self._add_account(objects.env, company, account, periods)


AnalyticAccountMonthReportXlsx(
    'report.analytic.account.month.report.xlsx',
    'account.analytic.account.month.report.wizard')
