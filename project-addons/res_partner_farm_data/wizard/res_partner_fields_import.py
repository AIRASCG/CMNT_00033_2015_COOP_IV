# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos All Rights Reserved
#    $Carlos Lombardía <carlos@comunitea.com>$
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

class FieldsImport(models.TransientModel):

    _name = 'res.partner.fields.import'

    def _get_control(self):
        return self._context.get('active_id', False)

    import_file = fields.Binary('File to import', required=True)
    control = fields.Many2one('res.partner', 'Control', default=_get_control)

    @api.multi
    def import_control(self):
        try:
            file = base64.b64decode(self.import_file)
            data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read())
            sh = data.sheet_by_index(0)
            header = sh.row_values(0)
            for line in range(1, sh.nrows):
                row = sh.row_values(line)
                control_vals = {'partner_id': self._context.get('active_id', \
                                                               False)}
                province_ids = self.env['res.country.state'].search(
                                            [('code', '=', str(int(row[0])))])
                control_vals['province_id'] = province_ids.id
                control_vals['townhall_id'] = str(int(row[1]))
                if row[2] == 0:
                    control_vals['added'] = False
                elif row[2] == 1:
                    control_vals['added'] = True
                control_vals['zone'] = int(row[3])
                control_vals['industrial_estate'] = str(int(row[4]))
                # control_vals['plot'] = str(int(row[5]))
                control_vals['enclosure'] = str(int(row[6]))
                control_vals['use'] = row[7]
                control_vals['sixpac_surface'] = row[8]
                control_vals['cap'] = row[9]
                control_vals['declared_surface'] = row[10]
                control_vals['net_surface'] = row[11]
                control_vals['product_code'] = str(int(row[12]))
                control_vals['product_name'] = row[13]
                control_vals['variety'] = int(row[14])
                control_vals['location_name'] = row[15]
                if row[16] == 'X':
                    control_vals['rent'] = True
                else:
                    control_vals['rent'] = False
                self.env['res.partner.fields'].create(control_vals)

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
