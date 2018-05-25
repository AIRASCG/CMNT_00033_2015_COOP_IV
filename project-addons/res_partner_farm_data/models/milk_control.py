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
import openerp.addons.decimal_precision as dp
from cairoplot import VerticalBarPlot
import base64
from zeep import Client
from datetime import datetime, timedelta


def average(lst):
    if not lst:
        return 0
    return reduce(lambda x, y: x + y, lst) / len(lst)


class MilkControl(models.Model):

    _name = 'milk.control'

    date = fields.Datetime('Date', required=True)
    exploitation_id = fields.\
        Many2one('res.partner', 'Exploitation', required=True,
                 default=lambda self: self.env.user.company_id.partner_id.id)
    state = fields.Selection(
        (('correct', 'Correct'), ('incorrect', 'Incorrect')), 'State')
    company_id = fields.Many2one("res.company", readonly=True,
                                 related="exploitation_id.company_id")
    line_ids = fields.One2many('milk.control.line', 'control_id', 'Lines')
    num_records = fields.Integer('Number of records',
                                 compute='_get_num_records')
    exception_txt = fields.Text("Exceptions", readonly=True)
    notes = fields.Text()

    @api.multi
    def _get_num_records(self):
        for obj in self:
            obj.num_records = len(obj.line_ids)

    @api.model
    def action_api_import_cron(self):
        #PREPROD
        #url_base = "http://213.60.254.109:85/Services/"
        #PROD
        url_base = "http://www.cegacol.com/Services/"
        url_api = url_base + "WsCatalogue.asmx?WSDL"
        client = Client(url_api)
        header = client.get_element("{" + url_base + "}AuthSoapHeader")

        milk_control_service = self.env.\
            ref('res_partner_farm_data.service_control_lechero')
        passwds = self.env['res.partner.passwd'].search(
            [('service', '=', milk_control_service.id)])
        for passwd in passwds:
            if not passwd.passwd or not passwd.name:
                continue
            header_value = header(UserName=passwd.name,
                                  Password=passwd.
                                  read(['passwd'])[0]['passwd'])
            client.set_default_soapheaders([header_value])
            last_sync_date = passwd.last_sync_date
            end_date = datetime.strptime(fields.Date.today(), "%Y-%m-%d").\
                date()
            if last_sync_date:
                start_date = datetime.\
                    strptime(last_sync_date, "%Y-%m-%d").date() + \
                    timedelta(1)
            else:
                start_date = end_date
                start_date.day = 1
                start_date.month = 1
                start_date = start_date.date()
            delta = end_date - start_date
            for i in range(delta.days + 1):
                vals = {}
                filter_date = start_date + timedelta(days=i)
                try:
                    data = client.service.\
                        Controles(
                            dateInterval={'DateFrom': filter_date,
                                          'DateTo': filter_date},
                            idRangeQuery=0, status=0)
                except Exception, e:
                    self.create({'date': filter_date.strftime("%Y-%m-%d"),
                                 'exploitation_id': passwd.partner_id.id,
                                 'state': 'incorrect',
                                 'exception_txt': e.message})
                    break
                if not data['ListResult']:
                    if data['MessageType']['Id'] != 30010:
                        self.create({'date': filter_date.strftime("%Y-%m-%d"),
                                     'exploitation_id': passwd.partner_id.id,
                                     'state': 'incorrect',
                                     'exception_txt':
                                     data['MessageType']['Description']})
                    else:
                        continue
                else:
                    milk_control = self.\
                        create({'date': filter_date.strftime("%Y-%m-%d"),
                                'exploitation_id': passwd.partner_id.id,
                                'state': 'correct'})
                    for cow_data in data['ListResult']['Control']:
                        vals = {'control_id': milk_control.id,
                                'cea': cow_data['Cea'],
                                'cib': cow_data['Cib'],
                                'name': cow_data['Nombre'],
                                'date_birth': cow_data['FechaParto'].date().
                                strftime("%Y-%m-%d"),
                                'birth_number': cow_data['NumeroParto'],
                                'control_number': cow_data['NumeroControl'],
                                'days': (cow_data['FechaControl'] -
                                cow_data['FechaParto']).days,
                                'milk_liters': cow_data['LecheKilos'],
                                'fat': cow_data['Grasa'],
                                'protein': cow_data['Proteina'],
                                'rcs': int(cow_data['RCS']),
                                'urea': int(cow_data['Urea'])}
                        vals['cumulative_milk'] = \
                            int(vals['milk_liters'] * vals['days'])
                        self.env['milk.control.line'].create(vals)
                    passwd.last_sync_date = filter_date.strftime("%Y-%m-%d")


class MilkControlLine(models.Model):

    _name = 'milk.control.line'

    control_id = fields.Many2one('milk.control', 'Control')
    cea = fields.Char('CEA')
    cib = fields.Char('CIB')
    crotal = fields.Char('crotal corto')
    name = fields.Char('Name')
    date_birth = fields.Date('Date of birth')
    birth_number = fields.Integer('Number of births')
    control_number = fields.Integer('Number of controls')
    days = fields.Integer('DEL')
    milk_liters = fields.Float('Milk liters')
    fat = fields.Float('Fat %')
    protein = fields.Float('Protein %')
    rcs = fields.Integer('RCS')
    urea = fields.Integer('Urea')
    cumulative_milk = fields.Integer('')
    cumulative_fat = fields.Float('')
    cumulative_protein = fields.Float('')


    def get_liters(self, type):
        if type == 'total':
            return self.milk_liters
        elif type == 'morning':
            return self.milk_liters * 1.8
        else:
            return self.milk_liters * 2.1

MILKING_TYPES = (('total', 'Total'), ('morning', 'morning Liters'),
                 ('late', 'late_liters'))

class MilkControlReport(models.Model):

    _name = 'milk.control.report'

    exploitation_1 = fields.Many2one('res.partner', 'Exploitation 1',
                                     required=True,
                                     domain=[('farm', '=', True),
                                             ('is_cooperative','=',False)])
    exploitation_2 = fields.Many2one('res.partner', 'Exploitation 2',
                                     domain=[('farm', '=', True),
                                             ('is_cooperative','=',False)])
    from_date = fields.Date('From date', required=True)
    to_date = fields.Date('To date', required=True)

    milking_type_1 = fields.Selection(MILKING_TYPES, required=True)
    milking_type_2 = fields.Selection(MILKING_TYPES)
    primerizas_cant_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_litros_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_grasa_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_proteina_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_celulas_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_urea_1 = fields.Float()
    adultas_cant_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_litros_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_grasa_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_proteina_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_celulas_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_urea_1 = fields.Float()
    total_cant_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_litros_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_grasa_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_proteina_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_celulas_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_urea_1 = fields.Float()
    vacas_invertidas_1 = fields.Char(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    coeficiente_persistencia_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    leche_corregida_a_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prod_media_lact_acumulada_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_medio_partos_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    relacion_grasa_prot_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_novillas_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_novillas_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_novillas_pico_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_adultas_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_adultas_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_adultas_pico_del_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    relacion_entre_picos_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_num_animales_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_porcen_animales_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_media_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_litros_total_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_num_animales_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_porcen_animales_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_media_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_litros_total_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_num_animales_1 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_porcen_animales_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_media_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_litros_total_1 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_cant_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_litros_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_grasa_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_proteina_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_celulas_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    primerizas_urea_2 = fields.Float()
    adultas_cant_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_litros_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_grasa_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_proteina_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_celulas_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    adultas_urea_2 = fields.Float()
    total_cant_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_litros_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_grasa_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_proteina_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_celulas_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    total_urea_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    vacas_invertidas_2 = fields.Char(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    coeficiente_persistencia_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    leche_corregida_a_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prod_media_lact_acumulada_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_medio_partos_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    relacion_grasa_prot_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_novillas_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_novillas_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_novillas_pico_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_adultas_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    pico_adultas_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    num_adultas_pico_del_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    relacion_entre_picos_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_num_animales_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_porcen_animales_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_media_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    prim_terc_lact_litros_total_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_num_animales_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_porcen_animales_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_media_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    seg_terc_lact_litros_total_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_num_animales_2 = fields.Integer(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_porcen_animales_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_media_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    terc_terc_lact_litros_total_2 = fields.Float(compute='_calculate_vals', digits=dp.get_precision('milk_report'))
    graphic_img = fields.Binary(compute='_calculate_vals')

    def _get_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', 'Company', default=_get_company)


    @api.multi
    def _get_data(self, num):
        self.ensure_one()
        suffix = u'_%s' % num
        milk_control = self.env['milk.control'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date), ('exploitation_id', '=', self['exploitation%s' % suffix].id)])
        milk_data = milk_control.mapped('line_ids')
        if not milk_data:
            return
        self['primerizas_cant%s' % suffix] = sum([1 for x in milk_data if x.cib and x.birth_number == 1])
        self['primerizas_del%s' % suffix] = average([x.days for x in milk_data if x.birth_number == 1])
        self['primerizas_litros%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number == 1])
        self['primerizas_grasa%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.fat / 100) for x in milk_data if x.birth_number == 1 and x.fat > 0]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.fat > 0 and x.birth_number == 1]) or 1.0)) * 100
        self['primerizas_proteina%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.protein / 100) for x in milk_data if x.birth_number == 1 and x.protein > 0]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.protein > 0 and x.birth_number == 1]) or 1.0)) * 100
        self['primerizas_celulas%s' % suffix] = sum([x.rcs * 1000 * x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number == 1]) / ((sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number == 1 and x.fat > 0]) or 1.0) * 1000)


        self['adultas_cant%s' % suffix] = sum([1 for x in milk_data if x.birth_number > 1])
        self['adultas_del%s' % suffix] = average([x.days for x in milk_data if x.birth_number > 1])
        self['adultas_litros%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1])


        self['adultas_grasa%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.fat / 100) for x in milk_data if x.birth_number > 1 and x.fat > 0]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1 and x.fat > 0]) or 1.0)) * 100
        self['adultas_proteina%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.protein / 100) for x in milk_data if x.birth_number > 1 and x.protein > 0]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1 and x.protein > 0]) or 1.0)) * 100
        self['adultas_celulas%s' % suffix] = sum([x.rcs * 1000 * x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1]) / ((sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1 and x.fat > 0]) or 1.0) * 1000)


        self['total_cant%s' % suffix] = sum([1 for x in milk_data if x.get_liters(self['milking_type%s' % suffix]) > 0])
        self['total_del%s' % suffix] = average([float(x.days) for x in milk_data])
        self['total_litros%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data])
        self['total_grasa%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.fat / 100) for x in milk_data]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data]) or 1.0)) * 100
        self['total_proteina%s' % suffix] = (sum([x.get_liters(self['milking_type%s' % suffix]) * (x.protein / 100) for x in milk_data]) / (sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data]) or 1.0)) * 100
        self['total_celulas%s' % suffix] = sum([x.rcs * 1000 * x.get_liters(self['milking_type%s' % suffix]) for x in milk_data]) / ((sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.fat > 0]) or 1.0) * 1000)

        invertidas = sum([1 for x in milk_data if x.protein > x.fat])
        self['vacas_invertidas%s' % suffix] =  '%s (%0.2f%%)' % (invertidas, (float(invertidas) / (self['total_cant%s' % suffix] or 1.0)) * 100)

        coeff = (
            average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.days > 179 and x.days < 306])
            - average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.days > 29 and x.days < 91])) \
            / ((average([x.days for x in milk_data if x.days > 179 and x.days < 306])
               - average([x.days for x in milk_data if x.days > 29 and x.days < 91])) or 1.0)

        # TODO: Cambiar 165 por campo !!!!!

        self['coeficiente_persistencia%s' % suffix] = coeff


        self['leche_corregida_a_del%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data]) + ((165 - average([x.days for x in milk_data])) * coeff)
        self['prod_media_lact_acumulada%s' % suffix] = average([x.cumulative_milk for x in milk_data]) / (average([x.days for x in milk_data]) or 1.0)
        self['num_medio_partos%s' % suffix] = average([float(x.birth_number) for x in milk_data])
        self['relacion_grasa_prot%s' % suffix] = self['total_grasa%s' % suffix] / (self['total_proteina%s' % suffix] or 1.0)

        self['pico_novillas%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number == 1 and x.days > 29 and x.days < 91])
        self['pico_novillas_del%s' % suffix] = average([x.days for x in milk_data  if x.birth_number == 1 and x.days > 29 and x.days < 91])
        self['num_novillas_pico_del%s' % suffix] = sum([1 for x in milk_data  if x.birth_number == 1 and x.days > 29 and x.days < 91])

        self['pico_adultas%s' % suffix] = average([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.birth_number > 1 and x.days > 29 and x.days < 61])
        self['pico_adultas_del%s' % suffix] = average([x.days for x in milk_data  if x.birth_number > 1 and x.days > 29 and x.days < 61])
        self['num_adultas_pico_del%s' % suffix] = sum([1 for x in milk_data  if x.birth_number > 1 and x.days > 29 and x.days < 61])
        if self['pico_adultas%s' % suffix]:
            self['relacion_entre_picos%s' % suffix] = self['pico_novillas%s' % suffix] / (self['pico_adultas%s' % suffix] or 1.0)
        else:
            self['relacion_entre_picos%s' % suffix] = 0

        self['prim_terc_lact_num_animales%s' % suffix] = len(milk_data.filtered(lambda r: r.days < 91))
        self['prim_terc_lact_porcen_animales%s' % suffix] = (self['prim_terc_lact_num_animales%s' % suffix] / (float(len(milk_data)) or 1.0)) * 100
        self['prim_terc_lact_litros_total%s' % suffix] = sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.days < 91])
        self['prim_terc_lact_media%s' % suffix] = self['prim_terc_lact_litros_total%s' % suffix] / (self['prim_terc_lact_num_animales%s' % suffix] or 1.0)
        self['seg_terc_lact_num_animales%s' % suffix] = len(milk_data.filtered(lambda r: r.days > 90 and r.days < 181))
        self['seg_terc_lact_porcen_animales%s' % suffix] = (self['seg_terc_lact_num_animales%s' % suffix] / (float(len(milk_data)) or 1.0)) * 100
        self['seg_terc_lact_litros_total%s' % suffix] = sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.days > 90 and x.days < 181])
        self['seg_terc_lact_media%s' % suffix] = self['seg_terc_lact_litros_total%s' % suffix] / (self['seg_terc_lact_num_animales%s' % suffix] or 1.0)
        self['terc_terc_lact_num_animales%s' % suffix] = len(milk_data.filtered(lambda r : r.days > 180))
        self['terc_terc_lact_porcen_animales%s' % suffix] = (self['terc_terc_lact_num_animales%s' % suffix] / (float(len(milk_data)) or 1.0)) * 100
        self['terc_terc_lact_litros_total%s' % suffix] = sum([x.get_liters(self['milking_type%s' % suffix]) for x in milk_data if x.days > 180])
        self['terc_terc_lact_media%s' % suffix] = self['terc_terc_lact_litros_total%s' % suffix] / (self['terc_terc_lact_num_animales%s' % suffix] or 1.0)




    @api.multi
    def _calculate_vals(self):
        for report in self:
            report._get_data(1)
            report._get_data(2)

        milk_control_1 = self.env['milk.control'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date), ('exploitation_id', '=', self.exploitation_1.id)])
        milk_data_1 = milk_control_1.mapped('line_ids')
        if self.exploitation_2:
            milk_control_2 = self.env['milk.control'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date), ('exploitation_id', '=', self.exploitation_2.id)])
            milk_data_2 = milk_control_2.mapped('line_ids')
        if not milk_data_1:
            return
        graph_vals = []
        for vals  in [(0, 31), (30, 91), (90, 121), (120, 181), (180, 241), (240, 305)]:
            av = average([x.get_liters(self.milking_type_1) for x in milk_data_1 if x.days > vals[0] and x.days < vals[1]])
            cont = sum([1 for x in milk_data_1 if x.days > vals[0] and x.days < vals[1] and x.get_liters(self.milking_type_1) > 0])
            if self.exploitation_2:
                av_2 = average([x.get_liters(self.milking_type_2) for x in milk_data_2 if x.days > vals[0] and x.days < vals[1]])
                cont_2 = sum([1 for x in milk_data_2 if x.days > vals[0] and x.days < vals[1] and x.get_liters(self.milking_type_2) > 0])
                graph_vals.append([round(av, 2), cont, round(av_2, 2), cont_2])
            else:
                graph_vals.append([round(av, 2), cont])

        av = average([x.get_liters(self.milking_type_1) for x in milk_data_1 if x.days > 305])
        cont = sum([1 for x in milk_data_1 if x.days > 305 and x.get_liters(self.milking_type_1) > 0])
        if self.exploitation_2:
            av_2 = average([x.get_liters(self.milking_type_2) for x in milk_data_2 if x.days > 305])
            cont_2 = sum([1 for x in milk_data_2 if x.days > 305 and x.get_liters(self.milking_type_2) > 0])
            graph_vals.append([round(av, 2), cont, round(av_2, 2), cont_2])
        else:
            graph_vals.append([round(av, 2), cont])

        if not self.exploitation_2:
            y_vals = [x[0] for x in graph_vals] + [x[1] for x in graph_vals]
            series_labels=[u'Media(lts/vaca y dia)', u'n de animales']
            series_colors=['red', 'blue']
        else:
            y_vals = [x[0] for x in graph_vals] + [x[1] for x in graph_vals] + [x[2] for x in graph_vals] + [x[3] for x in graph_vals]
            series_labels=[u'Media(lts/vaca y dia) %s' % self.exploitation_1.name, u'n de animales %s' % self.exploitation_1.name, u'Media(lts/vaca y dia) %s' % self.exploitation_2.name, u'n de animales %s' % self.exploitation_2.name]
            series_colors=['red', 'blue', 'green', 'yellow']
        max_y = int(max(y_vals)) + 10
        min_y = int(min(y_vals)) - 5
        min_y = min_y > 0 and min_y or 0
        test = VerticalBarPlot("/tmp/object_way.png", graph_vals, 900, 700, display_values=True, series_labels=series_labels, series_colors=series_colors, y_bounds=[min_y, max_y], x_labels=['DEL <30', 'DE 31-90 DEL', 'DE 91-120 DEL', 'DE 121-180 DEL', 'DE 181-240 DEL', 'DE 241-305 DEL', 'DEL>305'], border=20)
        test.render()
        test.commit()
        f = open("/tmp/object_way.png", "rb")
        self.graphic_img = base64.b64encode(f.read())
