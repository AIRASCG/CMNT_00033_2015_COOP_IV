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

class MilkControlImport(models.TransientModel):

    _name = 'milk.control.import'

    def _get_control(self):
        return self._context.get('active_id', False)

    import_file = fields.Binary('File to import', required=True)
    control = fields.Many2one('milk.control', 'Control', default=_get_control)

    @api.multi
    def import_control(self):
        try:
            self.control.line_ids.unlink()
            file = base64.b64decode(self.import_file)
            data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read())
            sh = data.sheet_by_index(0)
            header = sh.row_values(0)
            for line in range(1, sh.nrows):
                row = sh.row_values(line)
                control_vals = {'control_id': self.control.id}
                control_vals['cea'] = row[0]
                control_vals['cib'] = row[1]
                control_vals['crotal'] = row[2]
                control_vals['name'] = row[3]
                date_birth = xlrd.xldate_as_tuple(row[4], data.datemode)[:-3]
                control_vals['date_birth'] = date(*date_birth)
                control_vals['birth_number'] = row[5]
                control_vals['control_number'] = row[6]
                control_vals['days'] = row[7]
                control_vals['milk_liters'] = row[8]
                control_vals['fat'] = row[9]
                control_vals['protein'] = row[10]
                control_vals['rcs'] = row[11]
                control_vals['urea'] = row[12]
                control_vals['cumulative_milk'] = row[13]
                control_vals['cumulative_fat'] = row[14]
                control_vals['cumulative_protein'] = row[15]
                self.env['milk.control.line'].create(control_vals)
            self.control.write({'state': 'correct', 'exception_txt': ''})
        except Exception as e:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    self.control.with_env(new_env).\
                        write({'state': 'incorrect',
                               'exception_txt': e.message})
                    self.control.line_ids.with_env(new_env).unlink()
                    new_env.cr.commit()
        finally:
            return {'type': 'ir.actions.act_window_close'}
