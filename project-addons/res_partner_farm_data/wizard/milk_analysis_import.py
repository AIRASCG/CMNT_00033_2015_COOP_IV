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
from openerp import models, fields, api, registry, exceptions
import base64
import xlrd
import StringIO
import requests
import logging
import ast
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


class MilkAnalysisImport(models.TransientModel):

    _name = 'milk.analysis.import'

    STATE_MAP = {
        'A': 'accepted',
        'R': 'rejected',
        'E': 'waiting',
    }

    def _get_analysis(self):
        return self._context.get('active_id', False)

    import_file = fields.Binary('File to import', required=True)
    analysis = fields.Many2one('milk.analysis', 'Analysis',
                               default=_get_analysis)
    milk_analysis_type = fields.Selection(
        (('ligal', 'LIGAL'), ('lila', 'LILA')),
        related='analysis.exploitation_id.milk_analysis_type')
    year = fields.Integer('Year')

    def get_positions(self):
        if self.milk_analysis_type == 'lila':
            return False, False, False, False, False, False, False, 0, False, \
                False, False, 1, 2, 3, 4, 5, False, 6, False
        else:
            return 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

    @api.multi
    def import_milk_analysis(self):
        try:
            self.analysis.line_ids.unlink()
            file = base64.b64decode(self.import_file)
            data = xlrd.open_workbook(
                file_contents=StringIO.StringIO(file).read())
            sh = data.sheet_by_index(0)
            header = sh.row_values(0)
            route_pos, id_pos, yearmonth_pos, sample_pos, recep_pos, \
                anal_pos, state_pos, fat_pos, prot_pos, dry_pos, bact_pos, \
                cs_pos, inh_pos, cryos_pos, urea_pos = self.get_positions()
            for line in range(1, sh.nrows):
                row = sh.row_values(line)
                analysis_vals = {}
                if self.milk_analysis_type == 'lila':
                    dates = row[sample_pos].split('/')
                    sample_date = dates[0] + '-' + str(self.year)
                    sample_date_list = [int(x) for x in sample_date.split('-')]
                    analysis_vals['sample_date'] = date(sample_date_list[2],
                                                        sample_date_list[1],
                                                        sample_date_list[0])
                    analysis_date = dates[1] + '-' + str(self.year)
                    analysis_date_list = [int(x) for x in
                                          analysis_date.split('-')]
                    analysis_vals['analysis_date'] = date(
                        analysis_date_list[2], analysis_date_list[1],
                        analysis_date_list[0])

                else:
                    sample_date = xlrd.xldate_as_tuple(row[sample_pos],
                                                       data.datemode)[:-3]
                    analysis_vals['sample_date'] = date(*sample_date)

                    recep_date = xlrd.xldate_as_tuple(row[recep_pos],
                                                      data.datemode)[:-3]
                    analysis_vals['reception_date'] = date(*recep_date)

                    an_date = xlrd.xldate_as_tuple(row[anal_pos],
                                                   data.datemode)[:-3]
                    analysis_vals['analysis_date'] = date(*an_date)
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
                    analysis_vals['state'] = self.STATE_MAP[row[state_pos]]
                if yearmonth_pos:
                    analysis_vals['yearmonth'] = row[yearmonth_pos]
                if route_pos:
                    analysis_vals['route'] = row[route_pos]
                if id_pos:
                    analysis_vals['analysis_line_id'] = row[id_pos]
                analysis_vals['analysis_id'] = self.analysis.id
                self.env['milk.analysis.line'].create(analysis_vals)
            self.analysis.write({'state': 'correct', 'exception_txt': ''})
        except Exception as e:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid,
                                              self.env.context)
                    self.analysis.with_env(new_env).\
                        write({'state': 'incorrect',
                               'exception_txt': e.message})
                    self.analysis.line_ids.with_env(new_env).unlink()
                    new_env.cr.commit()
        finally:
            return {'type': 'ir.actions.act_window_close'}

    @api.model
    def import_api_analysis(self):
        API = milk_analysis_api()
        ligal_service = self.env.ref('res_partner_farm_data.service_ligal')
        passwds = self.env['res.partner.passwd'].search(
            [('service', '=', ligal_service.id)])
        for passwd in passwds:
            if not passwd.token or \
                    datetime.strptime(passwd.expire_time,
                                      '%Y-%m-%d %H:%M:%S') <= \
                    datetime.now() + timedelta(seconds=60):
                token, expire_time = API.new_token(
                    passwd.name, passwd.read(['passwd'])[0]['passwd'])
                passwd.token = token
                passwd.expire_time = datetime.now() + \
                    timedelta(seconds=int(expire_time))
            API.token = passwd.token
            samples = API.get_sample_data(
                datetime.now() + timedelta(days=-90), datetime.now())
            analysis = {}
            for sample in samples:
                sample_id = sample['Code']
                sample_state = self.STATE_MAP[sample['Revision']['Abbreviation']]
                line = self.env['milk.analysis.line'].search(
                    [('analysis_line_id', '=', sample_id),
                     ('state', '=', sample_state)])
                if line:
                    continue
                if 'Customer' in sample:
                    vat = sample['Customer']['VATReg']
                    if vat[0] == '0':
                        vat = vat[1:]
                    if vat[-1].isalpha():
                        vat = vat[-1] + vat[:-1]
                    vat = 'ES'+vat
                    partner = self.env['res.partner'].search(
                        [('vat', '=', vat), ('farm', '=', True)])
                    if not partner:
                        logger.error('Not found partner with vat %s' % vat)
                        continue
                    if len(partner) > 1:
                        logger.error('Various partners with vat %s' % vat)
                        continue
                else:
                    partner = passwd.partner_id

                line_vals = {
                    'analysis_line_id': sample_id,
                    'route': sample['RelationRoute'],
                    'yearmonth': sample['Period'],
                    'sample_date': datetime.strptime(
                        sample['SampleDate'], '%Y-%m-%dT%H:%M:%S').date(),
                    'reception_date': datetime.strptime(
                        sample['ReceptionDate'], '%Y-%m-%dT%H:%M:%S').date(),
                    'analysis_date': datetime.strptime(
                        sample['AnalisysDate'], '%Y-%m-%dT%H:%M:%S').date(),
                    'state': sample_state
                }
                test_map = {
                    '_I00001': 'fat',
                    '_I00002': 'protein',
                    '_I00004': 'dry_extract',
                    '_I00005': 'bacteriology',
                    '_I00006': 'cs',
                    '_I00007': 'inhibitors',
                    '_I00008': 'cryoscope',
                    '_I00009': 'urea',
                }
                for test_code in test_map.keys():
                    if not sample[test_code]:
                        continue
                    test_val = ast.literal_eval(sample[test_code])['Result']
                    try:
                        if test_val == '-':
                            test_val = '0'
                        test_val = float(test_val.replace(',', '.'))
                    except:
                        pass
                    line_vals[test_map[test_code]] = test_val
                try:
                    if 'route' in line_vals:
                        float(line_vals['route'])
                    if 'fat' in line_vals:
                        float(line_vals['fat'])
                    if 'protein' in line_vals:
                        float(line_vals['protein'])
                    if 'dry_extract' in line_vals:
                        float(line_vals['dry_extract'])
                    if 'cryoscope' in line_vals:
                        float(line_vals['cryoscope'])
                except ValueError:
                    continue
                line = self.env['milk.analysis.line'].search(
                    [('analysis_line_id', '=', sample_id)])
                if line:
                    line.write(line_vals)
                else:
                    if partner.id not in analysis:
                        analysis[partner.id] = []
                    analysis[partner.id].append(line_vals)
            for partner_id in analysis.keys():
                self.env['milk.analysis'].create(
                    {'state': 'correct',
                     'exploitation_id': partner_id,
                     'date': datetime.now(),
                     'line_ids': [(0, 0, x) for x in analysis[partner_id]]})


class milk_analysis_api(object):

    url = 'https://www.ligal.net/Service'

    paths = {
        'auth': '/Token',
        'customers': '/api/customers',
        'samples': '/api/samples'
    }

    def __init__(self):
        self._token = ''
        self.skip = 0

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = 'bearer %s' % value

    def new_token(self, user, password):
        data = 'username=%s&password=%s&grant_type=password' % (user, password)
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        resp = requests.get(url=self.url + self.paths['auth'],
                            data=data, headers=headers)
        data = resp.json()
        if 'error' in data:
            raise exceptions.Warning(data['error'], data['error_description'])
        return data['access_token'], data['expires_in']

    def get_sample_data(self, from_date, to_date):
        params = {
            'Authorization': self.token,
            'sampleDateFilterType': '2',
            'fromDate': from_date.strftime('%Y-%m-%d'),
            'toDate': to_date.strftime('%Y-%m-%d'),
            'sampleTypeCode': 'I0',
            'orderBy': 'SampleDate',
            'top': 100000,
            'skip': 0,
        }
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': self.token}
        resp = requests.get(url=self.url + self.paths['samples'],
                            params=params, headers=headers)
        data = resp.json()
        return data['Items']
