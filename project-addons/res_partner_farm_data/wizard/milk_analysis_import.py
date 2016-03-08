# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, exceptions, _, registry
import base64
import xlrd
import StringIO
from datetime import date


class MilkAnalysisImport(models.TransientModel):

    _name = 'milk.analysis.import'

    def _get_analysis(self):
        return self._context.get('active_id', False)

    import_file = fields.Binary('File to import', required=True)
    analysis = fields.Many2one('milk.analysis', 'Analysis', default=_get_analysis)
    milk_analysis_type = fields.Selection((('ligal', 'LIGAL'), ('lila', 'LILA')), related='analysis.exploitation_id.milk_analysis_type')
    year = fields.Integer('Year')

    def get_positions(self):
        if self.milk_analysis_type == 'lila':
            return 0, False, False, False, 4, 5, 6, 7, 8, False, 10, \
                False, False, False, False, False, False, False
        else:
            return range(0, 18)

    @api.multi
    def import_milk_analysis(self):
        try:
            self.analysis.line_ids.unlink()
            file = base64.b64decode(self.import_file)
            data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read())
            sh = data.sheet_by_index(0)
            header = sh.row_values(0)
            date_pos, dni_pos, expl_pos, an_date, fat_pos, prot_pos, dry_pos, \
                bact_pos, cs_pos, inh_pos, cryos_pos, urea_pos, state_pos, \
                buty_pos, water_pos, yearmonth_pos, \
                route_pos, id_pos = self.get_positions()
            for line in range(1, sh.nrows):
                row = sh.row_values(line)
                analysis_vals = {}
                if self.milk_analysis_type == 'lila':
                    dates = row[date_pos].split('/')
                    sample_date = dates[0] + '-' + str(self.year)
                    sample_date_list = [int(x) for x in sample_date.split('-')]
                    analysis_vals['sample_date'] = date(sample_date_list[2], sample_date_list[1], sample_date_list[0])
                    analysis_date = dates[1] + '-' + str(self.year)
                    analysis_date_list = [int(x) for x in analysis_date.split('-')]
                    analysis_vals['analysis_date'] = date(analysis_date_list[2], analysis_date_list[1], analysis_date_list[0])

                else:
                    sample_date = xlrd.xldate_as_tuple(row[date_pos], data.datemode)[:-3]
                    analysis_vals['sample_date'] = date(*sample_date)
                    an_date = xlrd.xldate_as_tuple(row[an_date], data.datemode)[:-3]
                    analysis_vals['analysis_date'] = date(*an_date)
                if dni_pos:
                    analysis_vals['dni'] = row[dni_pos]
                if expl_pos:
                    analysis_vals['exploitation_name'] = row[expl_pos]
                if fat_pos:
                    analysis_vals['fat'] = row[fat_pos]
                if prot_pos:
                    analysis_vals['protein'] = row[prot_pos]
                if dry_pos:
                    analysis_vals['dry_extract'] = row[dry_pos]
                if bact_pos:
                    analysis_vals['bacteriology'] = row[bact_pos]
                if cs_pos:
                    analysis_vals['cs'] = row[cs_pos]
                if inh_pos:
                    analysis_vals['inhibitors'] = row[inh_pos]
                if cryos_pos:
                    analysis_vals['cryoscope'] = row[cryos_pos]
                if urea_pos:
                    analysis_vals['urea'] = row[urea_pos]
                if state_pos:
                    analysis_vals['state'] = row[state_pos]
                if buty_pos:
                    analysis_vals['butyric'] = row[buty_pos]
                if water_pos:
                    analysis_vals['water'] = row[water_pos]
                if yearmonth_pos:
                    analysis_vals['yearmonth'] = row[yearmonth_pos]
                if route_pos:
                    analysis_vals['route'] = row[route_pos]
                if expl_pos:
                    analysis_vals['analysis_line_id'] = row[id_pos]
                analysis_vals['analysis_id'] = self.analysis.id
                self.env['milk.analysis.line'].create(analysis_vals)
            self.analysis.write({'state': 'correct'})
        except:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    self.analysis.with_env(new_env).write({'state': 'incorrect'})
                    self.analysis.line_ids.with_env(new_env).unlink()
                    new_env.cr.commit()
        finally:
            return {'type': 'ir.actions.act_window_close'}
