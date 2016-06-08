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

from openerp import models, fields, api
from datetime import datetime
import os
import logging
import csv
_logger = logging.getLogger(__name__)


class DecodeDictReader(csv.DictReader):

    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", encoding=False, *args, **kwds):
        self.encoding = encoding
        return csv.DictReader.__init__(
            self, f, fieldnames=fieldnames, restkey=restkey,
            restval=restval, dialect=dialect, *args, **kwds)

    def next(self):
        res = csv.DictReader.next(self)
        final_dict = {}
        for rk in res.keys():
            final_dict[rk] = res[rk].decode(self.encoding)
        return final_dict

    @property
    def fieldnames(self):
        res = csv.DictReader.fieldnames.fget(self)
        return [x.decode(self.encoding) for x in res]


class GescarroData(models.Model):

    _name = 'gescarro.data'

    def _get_name_sequence(self):
        return self.env['ir.sequence'].get('gescarro.data')

    exploitation_id = fields.Many2one(
        'res.partner', 'Exploitation', required=True,
        default=lambda self: self.env.user.company_id.partner_id.id)
    company_id = fields.Many2one("res.company", readonly=True,
                                 related="exploitation_id.company_id")
    name = fields.Char(default=_get_name_sequence)
    date = fields.Date(required=True)
    milk_cows_lot = fields.Float()
    milking_cows = fields.Float()
    tank_cows = fields.Float()
    dry_cows_lot = fields.Float()
    tank_liters = fields.Float()
    retired_liters = fields.Float()
    kg_leftover = fields.Float()
    leftover_reused = fields.Float()
    minutes_first_ration = fields.Float()
    minutes_next_ration = fields.Float()
    first_ration_cost = fields.Float()
    next_ration_cost = fields.Float()
    fix_cost = fields.Float()
    wet_mixture = fields.Float()
    wet_mixture_ms = fields.Float('% MS')
    wet_mixture_ms_fodder = fields.Float('% MS fodder / MS total')
    wet_mixture_ms_concentrated = fields.Float('% MS concentrated / MS total')
    wet_mixture_enl = fields.Float('ENL (Mcal/Kg MS)')
    wet_raw_protein = fields.Float('Proteína bruta (% MS)')
    wet_cost = fields.Float('Cost (€/Ton MF)')
    lines = fields.One2many('gescarro.data.line', 'data_id')

    ms_fodder = fields.Float('% MS', compute='_get_calculated_vals')
    ms_kg_cow_fodder = fields.Float('MS (Kg/Cow)',
                                    compute='_get_calculated_vals')
    enl_fodder = fields.Float('ENL (Mcal/Kg MS)',
                              compute='_get_calculated_vals')
    raw_protein_fodder = fields.Float('Raw protein (% MS)',
                                      compute='_get_calculated_vals')
    cost_fodder = fields.Float('Cost (€/Ton MF)',
                               compute='_get_calculated_vals')
    ms_concentrated = fields.Float('% MS',
                                   compute='_get_calculated_vals')
    ms_kg_cow_concentrated = fields.Float('MS (Kg/Cow)',
                                          compute='_get_calculated_vals')
    enl_concentrated = fields.Float('ENL (Mcal/Kg MS)',
                                    compute='_get_calculated_vals')
    raw_protein_concentrated = fields.Float('Raw protein (% MS)',
                                            compute='_get_calculated_vals')
    cost_concentrated = fields.Float('Cost (€/Ton MF)',
                                     compute='_get_calculated_vals')

    total_ration_ms = fields.Float('% MS', compute='_get_calculated_vals')
    total_ration_intake = fields.Float('Intake (Kg MS/cow)',
                                       compute='_get_calculated_vals')
    total_ration_ms_fodder = fields.Float('% MS fodder / MS total',
                                          compute='_get_calculated_vals')
    total_ration_ms_concentrated = fields.Float('% MS concentrated / MS total',
                                                compute='_get_calculated_vals')
    total_ration_enl = fields.Float('ENL(Mcal/Kg MS)',
                                    compute='_get_calculated_vals')
    total_ration_raw_protein = fields.Float('Raw protein (% MS)',
                                            compute='_get_calculated_vals')
    total_ration_cost_eur_ton_mf = fields.Float('Cost (€/Ton MF)',
                                                compute='_get_calculated_vals')
    total_ration_cost_eur_ton_ms = fields.Float('Cost (€/Ton MS)',
                                                compute='_get_calculated_vals')
    total_cost_carriage = fields.Float('Carriage cost (€/cow and day)',
                                       compute='_get_calculated_vals')
    total_ration_cost = fields.Float('Ration cost (€/vaca and day)',
                                     compute='_get_calculated_vals')

    tank_average = fields.Float('Tank average (L/Cow)',
                                compute='_get_calculated_vals')
    present_cow_average = fields.Float('Present cow average (L/ Cow)',
                                       compute='_get_calculated_vals')
    milk_average = fields.Float('Milk average (L/Cow)',
                                compute='_get_calculated_vals')
    conversion_index = fields.Float('Conversion index (L/Kg MS)',
                                    compute='_get_calculated_vals')
    tank_liter_cost = fields.Float('Tank liter cost (€/L)',
                                   compute='_get_calculated_vals')
    produced_liter_cost = fields.Float('Produced liter cost €/l',
                                       compute='_get_calculated_vals')
    fat = fields.Float('Fat (%)')
    protein = fields.Float('Protein (%)')
    urea = fields.Float('Urea (mg/kg)')

    @api.multi
    def calculate_vals(self, type):
        self.ensure_one()
        ms_field = 'ms_' + type
        ms_kg_cow_field = 'ms_kg_cow_' + type
        enl_field = 'enl_' + type
        raw_protein_field = 'raw_protein_' + type
        cost_field = 'cost_' + type
        total_kg = total_ms = total_ms_enl = total_ms_protein = total_cost = 0
        for line in self.lines.filtered(lambda r: r.type == type):
            total_kg += line.kg
            ms_x_kg = line.ms * line.kg
            total_ms += ms_x_kg
            total_ms_enl += ms_x_kg * line.enl
            total_ms_protein += ms_x_kg * line.raw_protein
            total_cost = line.cost * line.kg
        if total_kg:
            self[ms_field] = total_ms / total_kg
            self[cost_field] = total_cost / total_kg
        else:
            self[ms_field] = 0.0
            self[cost_field] = 0.0
        if self.milk_cows_lot:
            self[ms_kg_cow_field] = total_ms / (self.milk_cows_lot * 100)
        else:
            self[ms_kg_cow_field] = 0.0
        if total_ms:
            self[enl_field] = total_ms_enl / total_ms
            self[raw_protein_field] = total_ms_protein / total_ms
        else:
            self[enl_field] = 0.0
            self[raw_protein_field] = 0.0

    @api.multi
    def _get_calculated_vals(self):
        try:
            for data in self:
                for type in ['fodder', 'concentrated']:
                    data.calculate_vals(type)
                if not data.wet_mixture:
                    data.total_ration_ms = (data.ms_kg_cow_fodder *
                                            data.ms_fodder +
                                            data.ms_kg_cow_concentrated *
                                            data.ms_concentrated) / \
                        (data.ms_kg_cow_concentrated + data.ms_kg_cow_fodder)
                    if not data.leftover_reused:
                        total_leftover = data.kg_leftover
                    else:
                        last_gescarro = self.env['gescarro.data'].search(
                            [('exploitation_id', '=',
                              data.exploitation_id.id)],
                            order='date desc', limit=1)
                        if last_gescarro:
                            total_leftover = data.kg_leftover + \
                                last_gescarro.kg_leftover
                        else:
                            total_leftover = data.kg_leftover
                    data.total_ration_intake = data.ms_kg_cow_fodder + \
                        data.ms_kg_cow_concentrated + \
                        (((total_leftover) * data.total_ration_ms) /
                         (data.milk_cows_lot * 100))
                    data.total_ration_ms_fodder = (data.ms_fodder /
                                                   (data.ms_fodder +
                                                    data.ms_concentrated)) * \
                        100
                    data.total_ration_ms_concentrated = (data.ms_concentrated
                                                         / (data.ms_fodder +
                                                            data.ms_concentrated
                                                            )) * 100
                    data.total_ration_enl = (data.ms_kg_cow_fodder *
                                             data.enl_fodder +
                                             data.ms_kg_cow_concentrated *
                                             data.enl_concentrated) / \
                        (data.ms_kg_cow_fodder + data.ms_kg_cow_concentrated)
                    data.total_ration_raw_protein = \
                        (data.ms_kg_cow_fodder * data.raw_protein_fodder +
                         data.ms_kg_cow_concentrated *
                         data.raw_protein_concentrated) / \
                        (data.ms_kg_cow_fodder + data.ms_kg_cow_concentrated)
                    data.total_ration_cost_eur_ton_mf = \
                        (data.cost_fodder * (data.ms_kg_cow_fodder /
                                             data.ms_fodder) +
                         data.cost_concentrated * (data.ms_kg_cow_concentrated
                                                   / data.ms_concentrated)) / \
                        ((data.ms_kg_cow_fodder/data.ms_fodder) +
                         (data.ms_kg_cow_concentrated / data.ms_concentrated))
                    data.total_ration_cost_eur_ton_ms = \
                        (data.total_ration_cost_eur_ton_mf /
                         (data.total_ration_ms / 100))
                    data.total_cost_carriage = \
                        (data.minutes_first_ration * data.first_ration_cost +
                         data.minutes_next_ration * data.next_ration_cost +
                         data.fix_cost) / data.milk_cows_lot
                else:
                    data.total_ration_ms = data.wet_mixture_ms
                    if not data.leftover_reused:
                        total_leftover = data.kg_leftover
                    else:
                        last_gescarro = self.env['gescarro.data'].search(
                            [('exploitation_id', '=',
                              data.exploitation_id.id)],
                            order='date desc', limit=1)
                        if last_gescarro:
                            total_leftover = data.kg_leftover + \
                                last_gescarro.kg_leftover
                        else:
                            total_leftover = data.kg_leftover
                    data.total_ration_intake = (data.wet_mixture_ms *
                                                data.wet_mixture_ms) / \
                        (data.milk_cows_lot * 100)
                    data.total_ration_ms_fodder = data.wet_mixture_ms_fodder
                    data.total_ration_ms_concentrated = \
                        data.wet_mixture_ms_concentrated
                    data.total_ration_enl = data.wet_mixture_enl
                    data.total_ration_raw_protein = data.wet_raw_protein
                    data.total_ration_cost_eur_ton_mf = data.wet_cost
                    data.total_ration_cost_eur_ton_ms = data.wet_mixture_ms / \
                        data.wet_cost
                    data.total_cost_carriage = 0.0
                data.total_ration_cost = data.total_ration_intake * \
                    data.total_ration_cost_eur_ton_ms / 1000 + \
                    data.total_cost_carriage
                data.tank_average = data.tank_liters / data.tank_cows
                data.present_cow_average = (data.tank_liters +
                                            data.retired_liters) / \
                    (data.milk_cows_lot + data.dry_cows_lot)
                data.milk_average = (data.tank_liters +
                                     data.retired_liters) / data.milking_cows
                data.conversion_index = data.milk_average / \
                    data.total_ration_intake
                data.tank_liter_cost = (data.total_ration_cost *
                                        data.tank_cows) / data.tank_liters
                data.produced_liter_cost = (data.total_ration_cost *
                                            data.milking_cows) / \
                    (data.tank_liters + data.retired_liters)
        except ZeroDivisionError:
            pass

    @api.multi
    def get_milk_analysis_vals(self):
        for gescarro in self:
            analysis_line = self.env['milk.analysis.line'].search(
                [('sample_date', '=', gescarro.date),
                 ('analysis_id.exploitation_id', '=',
                  gescarro.exploitation_id.id)])
            if analysis_line:
                gescarro.write({'fat': analysis_line[0].fat,
                                'protein': analysis_line[0].protein,
                                'urea': analysis_line[0].urea})

    @api.model
    def import_ftp_data(self):
        folder = self.env['ir.config_parameter'].get_param('gescarro.folder')
        if not folder:
            _logger.error('Not found config parameter %s' % 'gescarro.folder')
            return
        importation_folder = '%s%slecturas' % (folder, os.sep)
        process_folder = '%s%sprocesados' % (folder, os.sep)
        if 'lecturas' not in os.listdir(folder):
            os.mkdir(importation_folder)
        if 'procesados' not in os.listdir(folder):
            os.mkdir(process_folder)
        csv_files = [x for x in os.listdir(importation_folder)
                     if x.endswith('.csv')]
        for csv_file in csv_files:
            file_dir = importation_folder + os.sep + csv_file
            with open(file_dir, 'rb') as csv_content:
                freader = DecodeDictReader(csv_content, delimiter=';',
                                           quotechar='"',
                                           encoding='iso8859-15')
                line_names = freader.fieldnames[2:]
                date_field = freader.fieldnames[0]
                partner_field = freader.fieldnames[1]

                for row in freader:
                    exploitation_ref = row[partner_field]
                    exploitation = self.env['res.partner'].search(
                        [('ref', '=', exploitation_ref)])
                    if len(exploitation) != 1:
                        _logger.error(
                            'Not found a partner with reference %s' %
                            exploitation_ref)
                        continue

                    gescarro_vals = {
                        'date': datetime.strptime(
                            row[date_field], '%d/%m/%Y').date(),
                        'exploitation_id': exploitation.id,
                        'lines': []
                    }

                    for line_name in line_names:
                        kg = float(row[line_name].replace(',', '.'))
                        if not kg:
                            continue
                        line_vals = {'description': line_name,
                                     'kg': kg}

                        if line_name in [
                                u'Silo Maíz (Kg)', u'Silo Hierba (Kg)',
                                u'Silo Hierba 2 (Kg)', u'Alfalfa (Kg)',
                                u'Paja (Kg)', u'Hierba Seca (Kg)',
                                u'Veza (Kg)']:
                            line_vals['type'] = 'fodder'
                        else:
                            line_vals['type'] = 'concentrated'

                        gescarro_vals['lines'].append(
                            (0, 0, line_vals))
                    old_data = self.env['gescarro.data'].search(
                        [('date', '=', gescarro_vals['date']),
                         ('exploitation_id', '=',
                          gescarro_vals['exploitation_id'])])
                    if old_data:
                        for line in gescarro_vals.pop('lines'):
                            data_line = self.env['gescarro.data.line'].search(
                                [('description', '=', line[2]['description']),
                                 ('data_id', '=', old_data.id)])
                            if data_line:
                                data_line.kg += line[2]['kg']
                            else:
                                line[2]['data_id'] = old_data.id
                                self.env['gescarro.data.line'].create(line[2])
                    else:
                        self.env['gescarro.data'].create(gescarro_vals)
            os.rename(file_dir, process_folder + os.sep + csv_file)


class GescarroDataLine(models.Model):
    _name = 'gescarro.data.line'

    description = fields.Char()
    kg = fields.Float('Kg')
    ms = fields.Float('% MS')
    enl = fields.Float('ENL (Mcal/Kg MS)')
    raw_protein = fields.Float()
    cost = fields.Float('Cost (€/Ton MF)')
    data_id = fields.Many2one('gescarro.data', 'Data')
    type = fields.Selection((('fodder', 'fodder'),
                             ('concentrated', 'concentrated')), required=True)
