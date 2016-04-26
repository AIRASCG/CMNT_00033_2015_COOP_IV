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

from openerp import models, fields, api, exceptions, _
import base64
import xlrd
import StringIO
from datetime import date


class GescarroImport(models.TransientModel):

    _name = 'gescarro.import'

    import_file = fields.Binary('File to import', required=True)
    filename = fields.Char()


    @api.onchange('filename')
    def onchange_import_file(self):
        if self.filename:
            if len(self.filename) > 4 and self.filename[-4:] == '.xls':
                return
            raise exceptions.Warning(_('Filename error'), _('The file must be a .xls'))

    @api.multi
    def import_gescarro(self):
        file = base64.b64decode(self.import_file)
        data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read())
        sh = data.sheet_by_index(1)
        header = sh.row_values(7)
        number_of_lines = 20
        for line in range(9, sh.nrows):
            row = sh.row_values(line)
            gescarro_vals = {}
            if not row[11]:
                continue
            gescarro_date = xlrd.xldate_as_tuple(row[1], data.datemode)[:-3]
            gescarro_vals['date'] = date(*gescarro_date)
            gescarro_vals['milk_cows_lot'] = row[2]
            gescarro_vals['milking_cows'] = row[3]
            gescarro_vals['tank_cows'] = row[4]
            gescarro_vals['dry_cows_lot'] = row[5]
            gescarro_vals['tank_liters'] = row[6]
            gescarro_vals['retired_liters'] = row[7]
            gescarro_vals['kg_leftover'] = row[8]
            gescarro_vals['leftover_reused'] = row[9] # Esto es un booleano
            exp_ref = str(int(row[11]))
            exploitation = self.env['res.partner'].search([('ref', '=', exp_ref)])
            if not exploitation:
                raise exceptions.Warning(_('Import error'), _('Exploitation with reference %s not found') % exp_ref)
            gescarro_vals['exploitation_id'] = exploitation.id
            gescarro_vals['minutes_first_ration'] = row[12 + number_of_lines]
            gescarro_vals['minutes_next_ration'] = row[13 + number_of_lines]
            gescarro_vals['first_ration_cost'] = row[14 + number_of_lines]
            gescarro_vals['next_ration_cost'] = row[15 + number_of_lines]
            gescarro_vals['fix_cost'] = row[16 + number_of_lines]
            gescarro_vals['wet_mixture'] = row[17 + number_of_lines]
            gescarro_vals['wet_mixture_ms'] = row[18 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['wet_mixture_ms_fodder'] = row[19 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['wet_mixture_ms_concentrated'] = row[20 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['wet_mixture_enl'] = row[21 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['wet_raw_protein'] = row[22 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['wet_cost'] = row[23 + ((number_of_lines + 1)  * 4)]
            gescarro_vals['lines'] = []
            for sub_index in range(0, number_of_lines):
                data_init_pos = 12 + number_of_lines + 6 + (4 * sub_index)
                if not header[data_init_pos]:
                    continue
                subline = {}
                subline['kg'] = row[12 + sub_index]
                subline['description'] = header[data_init_pos].encode('utf-8')
                subline['ms'] = row[data_init_pos]
                subline['enl'] = row[data_init_pos + 1]
                subline['raw_protein'] = row[data_init_pos + 2]
                subline['cost'] = row[data_init_pos + 3]
                if header[data_init_pos].encode('utf-8') in \
                        ['SILO DE MAÍZ', 'SILO DE HIERBA', 'SILO DE HIERBA 2',
                         'ALFALFA', 'PAJA', 'HIERBA SECA', 'VEZA']:
                    subline['type'] = 'fodder'
                else:
                    subline['type'] = 'concentrated'
                gescarro_vals['lines'].append((0, 0, subline))
            gescarro_vals['lines'].append(
                (0, 0,
                 {'kg': row[10],
                  'description': header[118].encode('utf-8'),
                  'ms': row[118],
                  'enl': row[119],
                  'raw_protein': row[120],
                  'cost': row[121],
                  'type': 'concentrated',
                 }))
            gescarro = self.env['gescarro.data'].create(gescarro_vals)
            gescarro.get_milk_analysis_vals()
