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


class LotAnalysisImport(models.TransientModel):

    _name = 'lot.analysis.import'

    import_file = fields.Binary('File to import', required=True)

    @api.multi
    def import_analysis(self):
        file = base64.b64decode(self.import_file)
        data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read())
        sh = data.sheet_by_index(0)
        header = sh.row_values(0)
        for line in range(1, sh.nrows):
            row = sh.row_values(line)
            analysis_vals = {}
            lot_name = row[0]
            if isinstance(lot_name, float):
                lot_name = str(int(lot_name))
            elif isinstance(lot_name, int):
                lot_name = str(lot_name)
            lot = self.env['stock.production.lot'].search(
                [('name', '=', lot_name)])
            analysis_vals['lot_id'] = lot and lot.id or False
            analysis_vals['name'] = row[1]
            analysis_vals['tipo_material'] = row[2]
            ref_coop = str(row[3])
            coop_id = self.env['res.partner'].search([('ref', '=', ref_coop)])
            analysis_vals['cooperative_id'] = coop_id and coop_id.id or False
            ref_lab = str(row[4])
            lab_id = self.env['res.partner'].search([('ref', '=', ref_lab)])
            if lab_id:
                analysis_vals['lab_id'] = lab_id.id
            else:
                analysis_vals['lab_ref'] = ref_lab
            ref_exp = str(row[6])
            exp_id = self.env['res.partner'].search([('ref', '=', ref_exp)])
            analysis_vals['explotation_id'] = exp_id and exp_id.id or False
            analysis_vals['year'] = row[8]
            analysis_vals['product_name'] = row[9]
            analysis_vals['notes'] = row[10]
            sampling_date = xlrd.xldate_as_tuple(row[11], data.datemode)[:-3]
            analysis_vals['sampling_date'] = date(*sampling_date)
            analysis_date = xlrd.xldate_as_tuple(row[12], data.datemode)[:-3]
            analysis_vals['analysis_date'] = date(*analysis_date)

            analysis_vals['cut_number'] = row[13]
            analysis_vals['dry_material'] = row[14]
            analysis_vals['cinder'] = row[15]
            analysis_vals['enl'] = row[16]
            analysis_vals['ufl'] = row[17]
            analysis_vals['pb'] = row[18]
            analysis_vals['pbn'] = row[19]
            analysis_vals['ps'] = row[20]
            analysis_vals['starch'] = row[21]
            analysis_vals['grain_equivalence'] = row[22]
            analysis_vals['ee'] = row[23]
            analysis_vals['fb'] = row[24]
            analysis_vals['fad'] = row[25]
            analysis_vals['fnd'] = row[26]
            analysis_vals['lignina'] = row[27]
            analysis_vals['digestibility'] = row[28]
            analysis_vals['vrf'] = row[29]
            analysis_vals['pdie'] = row[30]
            analysis_vals['pdin'] = row[31]
            analysis_vals['ph'] = row[32]
            analysis_vals['ph_stability'] = row[33]
            analysis_vals['conservation_index'] = row[34]
            analysis_vals['lactic_acid'] = row[35]
            analysis_vals['acetic_acid'] = row[36]
            analysis_vals['butyric_acid'] = row[37]
            analysis_vals['ecoli_absence'] = bool(row[38])
            analysis_vals['ecoli_unquantifiable'] = bool(row[39])
            analysis_vals['ecoli_value'] = row[40]
            analysis_vals['salmonella_absence'] = bool(row[41])
            analysis_vals['salmonella_unquantifiable'] = bool(row[42])
            analysis_vals['salmonella_value'] = row[43]
            analysis_vals['staphylococci'] = row[44]
            analysis_vals['mold'] = row[45]
            analysis_vals['clostridium'] = row[46]
            analysis_vals['yeast'] = row[47]
            analysis_vals['enterobacteriaceae'] = row[48]
            analysis_vals['calcium'] = row[49]
            analysis_vals['phosphor'] = row[50]
            analysis_vals['sodium'] = row[51]
            analysis_vals['potassium'] = row[52]
            analysis_vals['magnesium'] = row[53]
            analysis_vals['iron'] = row[54]
            analysis_vals['copper'] = row[55]
            analysis_vals['zinc'] = row[56]
            analysis_vals['manganese'] = row[57]
            analysis_vals['chlorine'] = row[58]
            analysis_vals['sulfur'] = row[59]
            analysis_vals['zearelenone'] = row[60]
            analysis_vals['vomitoxin'] = row[61]
            analysis_vals['afla_b1'] = row[62]
            self.env['lot.analysis'].create(analysis_vals)
        return {'type': 'ir.actions.act_window_close'}
