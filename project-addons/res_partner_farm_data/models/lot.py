# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea All Rights Reserved
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
from openerp import models, fields, api, _, exceptions
from datetime import datetime


class LotPartnerName(models.Model):

    _name = 'lot.partner.name'

    name = fields.Char()
    sequence = fields.Integer()
    lot_id = fields.Many2one('lot.partner')


class LotPartner(models.Model):

    _name = 'lot.partner'
    _inherit = ['yearly.data']

    lot_number = fields.Integer('Lot number')
    lot_names = fields.One2many('lot.partner.name', 'lot_id')

    _sql_constraints = [
        ('lot_uniq', 'unique (year_id,farm_id)',
         _('Error! Only one lot by year and company.'))
    ]

    '''@api.one
    @api.constrains('lot_names')
    def _check_lot_names(self):
        for lot in self:
            if len(lot.lot_names) > lot.lot_number:
                raise exceptions.ValidationError(_(''), _(''))
            if sorted([x.sequence for x in lot.lot_names]) != range(1, lot.lot_number + 1):
                raise exceptions.ValidationError(_(''), _(''))'''


class Lot(models.Model):

    _name = 'lot'

    date = fields.Datetime('Date', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default=lambda a: datetime.now())
    user_id = fields.Many2one('res.users', 'User', required=True,
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user.id)
    farm_id = fields.Many2one('res.partner', 'Farm', required=True,
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self:
                              self.env.user.company_id.partner_id.id)
    state = fields.Selection(
        (('draft', 'Draft'), ('validated', 'Validated')), 'State',
        default='draft')
    notes = fields.Text()
    lot_number = fields.Char('Lot number', compute='_get_lot_data',
                             readonly=True,
                             states={'draft': [('readonly', False)]})
    lot_details = fields.One2many('lot.detail', 'lot_id', 'Lot details',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})

    total_liters_sold = fields.Integer('Total liters sold',
                                       readonly=True,
                                       states={'draft': [('readonly', False)]})
    number_milking_cows = fields.Integer('Number of milking cows',
                                         readonly=True,
                                         compute='_get_lot_data')
    liters_produced_per_day = fields.Integer(
        'Liters produced per day', readonly=True, compute='_get_lot_data')
    cs = fields.Integer('CS (X1000)', readonly=True,
                        states={'draft': [('readonly', False)]})
    live_weight = fields.Integer('Live weight', readonly=True,
                                 states={'draft': [('readonly', False)]})
    collection_frequency = fields.Integer('Collection frequency',
                                          readonly=True,
                                          states={'draft':
                                                  [('readonly', False)]})
    number_dry_cows = fields.Integer(
        'Number of dry cows', readonly=True,
        states={'draft': [('readonly', False)]})
    liters_sold_per_day = fields.Integer('Liters sold per day',
                                         readonly=True,
                                         compute='_get_lot_data')
    milk_price = fields.Float('Milk price(€ / 1000L)',
                              readonly=True,
                              states={'draft': [('readonly', False)]})
    liters_discarded_per_day = fields.Integer('Liters discarded per day',
                                              readonly=True,
                                              states={'draft':
                                                      [('readonly', False)]})
    carriage_cost = fields.Integer('Carriage cost (€/month)', readonly=True,
                                   states={'draft': [('readonly', False)]})
    number_cubicle_lactation = fields.Integer(
        'Nº cubicle lactation', readonly=True,
        states={'draft': [('readonly', False)]})
    mg = fields.Float('%MG', readonly=True,
                      states={'draft': [('readonly', False)]})
    dry_cow_ration_cost = fields.Float('Dry cow ration cost(€/ cow and day)',
                                       readonly=True,
                                       states={'draft': [('readonly', False)]})
    liters_reused_day = fields.Integer('Liters reused/day', readonly=True,
                                       states={'draft': [('readonly', False)]})
    mp = fields.Float('%MP', readonly=True,
                      states={'draft': [('readonly', False)]})
    carriage_cost_cow_day = fields.Float('Carriage cost (€/ cow and day)',
                                         readonly=True, compute='_get_lot_data')
    urea = fields.Float('Urea')

    @api.multi
    def name_get(self):
        return [(x.id, u'{} - {}'.format(x.date, x.farm_id.name)) for x in self]

    @api.multi
    def _get_lot_data(self):
        for lot in self:
            lot_partner = self.env['lot.partner'].search(
                [('farm_id', '=', lot.farm_id.id),
                 ('year_id.date_start', '<=', lot.date),
                 ('year_id.date_stop', '>=', lot.date)])
            total_lots = lot_partner and lot_partner[0].lot_number or 0
            lot.lot_number = '%s/%s' % (len(lot.lot_details), total_lots)
            lot.number_milking_cows = sum(
                [x.number_milking_cows for x in lot.lot_details])
            lot.carriage_cost_cow_day = (lot.carriage_cost / 30.0) / \
                float((lot.number_milking_cows + lot.number_dry_cows) or 1.0)
            lot.liters_produced_per_day = sum(
                [x.tank_liters + x.liters_on_farm_consumption +
                 x.retired_liters for x in lot.lot_details])
            if lot.collection_frequency:
                lot.liters_sold_per_day = lot.total_liters_sold / lot.collection_frequency
            else:
                lot.liters_sold_per_day = 0

    @api.multi
    def button_validate(self):
        self.state = 'validated'

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def get_data_lot(self):
        self.ensure_one()
        last_lot = self.env['lot'].search(
            [('farm_id', '=', self.farm_id.id),
             ('id', '!=', self.id), ('date', '<=', self.date),
             ('state', '=', 'validated')],
            order='date desc', limit=1)
        for detail in last_lot.lot_details:
            new_detail = detail.copy({'lot_id': self.id, 'date': datetime.now(), 'lot_contents': False})
            for content in detail.lot_contents:
                content.copy(
                    {'detail_id': new_detail.id,
                     'manual_setted': True,
                     '_theorical_kg_ration': content.kg_ration,
                     '_theorical_ms': content.ms,
                     '_theorical_enl': content.enl,
                     '_theorical_pb': content.pb})
        self.collection_frequency = last_lot.collection_frequency
        self.number_cubicle_lactation = last_lot.number_cubicle_lactation
        self.milk_price = last_lot.milk_price
        self.carriage_cost = last_lot.carriage_cost
        self.dry_cow_ration_cost = last_lot.dry_cow_ration_cost
        self.live_weight = last_lot.live_weight
        analysis = self.env['milk.analysis.line'].search(
            [('analysis_id.exploitation_id', '=', self.farm_id.id),
             ('sample_date', '<=', self.date[:10])],
            order='sample_date desc', limit=1)
        self.urea = analysis.urea

    @api.multi
    def get_data_from_ligal(self):
        for lot in self:
            analysis_ids = self.env['milk.analysis.line'].\
                search([('analysis_id.exploitation_id', '=',
                         lot.farm_id.id), ('sample_date', '<=', lot.date),
                        ('state', '=', 'accepted')],
                       limit=3, order="sample_date desc")
            mg_total = mp_total = 0
            for line in analysis_ids:
                mg_total += line.fat or 0.0
                mp_total += line.protein or 0.0
            if mg_total:
                lot.mg = mg_total / len(analysis_ids)
            else:
                lot.mg = mg_total
            if mp_total:
                lot.mp = mp_total / len(analysis_ids)
            else:
                lot.mp = mp_total


class LotDetailSequence(models.Model):

    _name = 'lot.detail.sequence'

    name = fields.Integer('Name')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The sequence name must be unique !')
    ]


class LotDetail(models.Model):

    _name = 'lot.detail'

    name = fields.Char('Name', required=True)
    description = fields.Char('Description', required=True)
    user_id = fields.Many2one('res.users', 'User', required=True, readonly=True,
                              default=lambda self: self.env.user.id)
    lot_id = fields.Many2one('lot', 'Lot')

    lot_contents = fields.One2many('lot.content', 'detail_id', 'Content',
                                   copy=True)
    date = fields.Datetime('Date', required=True,
                           default=lambda a: datetime.now())
    notes = fields.Text()
    rations_make_number = fields.Integer('Number of maked rations')
    surplus = fields.Integer('Surplus (Kg)')
    cows_tank_number = fields.Integer('Cows tank number')
    liters_on_farm_consumption = fields.Integer('Liters on-farm consumption')
    kf_mf_carriage = fields.Integer('kf MF carriage', compute='_get_kf_mf_carraige', inverse='_set_kf_mf_carriage',
                                    help="No hace falta escribirlo, porque se calcula multiplicando el 'Nº de raciones hechas' "
                                         "por la suma de los 'KG/ración' de los ingredientes. Si se escribe, provocará que el campo "
                                         "'Nº de raciones hechas' sea calculado consecuentemente")
    cows_eat_number = fields.Integer('Cows eat number')
    tank_liters = fields.Integer('Tank liters')
    retired_liters = fields.Integer('Retired liters')
    number_milking_cows = fields.Integer('Milking cows')
    number_cubicles_in_lot = fields.Integer('Number of cubicles in this lot')
    kg_plucking = fields.Integer('Plucking kg')
    kg_plucking_theo = fields.Integer('Plucking kg theoric')
    ms_plucking = fields.Float()

    kg_mf_ration_theo = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    perc_ms_ration_theo = fields.Float('', compute='_get_lot_calcs',
                                       readonly=True)
    kg_ms_ration_theo = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    imf_theo = fields.Float('', compute='_get_lot_calcs', readonly=True)
    kg_plucking_cow_day_theo = fields.Float('', compute='_get_lot_calcs',
                                            readonly=True)
    ims_unifed_kg_cow_day_theo = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    ims_plucking_kg_cow_day_theo = fields.Float('', compute='_get_lot_calcs',
                                                readonly=True)
    ims_total_kg_cow_day_theo = fields.Float('', compute='_get_lot_calcs',
                                             readonly=True)
    ic_liters_kg_theo = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    ic_corrected_liters_kg_theo = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_enl_theo = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_pb_theo = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    real_production_deviation_theo = fields.Float('', compute='_get_lot_calcs',
                                                  readonly=True)
    ration_cost_eur_theo = fields.Float('', compute='_get_lot_calcs',
                                        readonly=True)
    ration_cost_eur_ton_mf_theo = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_cost_eur_ton_ms_theo = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_carriage_cost_eur_cow_day_theo = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_eur_liter_theo = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_corrected_milk_eur_liter_theo = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    kg_mf_ration_real = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    perc_ms_ration_real = fields.Float('', compute='_get_lot_calcs',
                                       readonly=True)
    kg_ms_ration_real = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    imf_real = fields.Float('', compute='_get_lot_calcs', readonly=True)
    kg_plucking_cow_day_real = fields.Float('', compute='_get_lot_calcs',
                                            readonly=True)
    ims_unifed_kg_cow_day_real = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    ims_plucking_kg_cow_day_real = fields.Float('', compute='_get_lot_calcs',
                                                readonly=True)
    ims_total_kg_cow_day_real = fields.Float('', compute='_get_lot_calcs',
                                             readonly=True)
    ic_liters_kg_real = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    ic_corrected_liters_kg_real = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_enl_real = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_pb_real = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    real_production_deviation_real = fields.Float('', compute='_get_lot_calcs',
                                                  readonly=True)
    ration_cost_eur_real = fields.Float('', compute='_get_lot_calcs',
                                        readonly=True)
    ration_cost_eur_ton_mf_real = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_cost_eur_ton_ms_real = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_carriage_cost_eur_cow_day_real = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_eur_liter_real = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_corrected_milk_eur_liter_real = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)

    kg_mf_ration_anal = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    perc_ms_ration_anal = fields.Float('')
    kg_ms_ration_anal = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    imf_anal = fields.Float('', compute='_get_lot_calcs', readonly=True)
    kg_plucking_cow_day_anal = fields.Float('', compute='_get_lot_calcs',
                                            readonly=True)
    ims_unifed_kg_cow_day_anal = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    ims_plucking_kg_cow_day_anal = fields.Float('', compute='_get_lot_calcs',
                                                readonly=True)
    ims_total_kg_cow_day_anal = fields.Float('', compute='_get_lot_calcs',
                                             readonly=True)
    ic_liters_kg_anal = fields.Float('', compute='_get_lot_calcs',
                                     readonly=True)
    ic_corrected_liters_kg_anal = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_enl_anal = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    milk_prediction_by_pb_anal = fields.Float('', compute='_get_lot_calcs',
                                              readonly=True)
    real_production_deviation_anal = fields.Float('', compute='_get_lot_calcs',
                                                  readonly=True)
    ration_cost_eur_anal = fields.Float('', compute='_get_lot_calcs',
                                        readonly=True)
    ration_cost_eur_ton_mf_anal = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_cost_eur_ton_ms_anal = fields.Float('', compute='_get_lot_calcs',
                                               readonly=True)
    ration_carriage_cost_eur_cow_day_anal = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_eur_liter_anal = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)
    ration_carriage_cost_corrected_milk_eur_liter_anal = fields.Float(
        '', compute='_get_lot_calcs', readonly=True)

    grs_fat_cow_day = fields.Float('', compute='_get_lot_calcs', readonly=True)
    grs_protein_cow_day = fields.Float('', compute='_get_lot_calcs',
                                       readonly=True)
    ingress_milk_cow_day = fields.Float('Ingress milk/milk cow and day',
                                        compute='_get_lot_calcs',
                                        readonly=True)
    feed_cost_cow_day = fields.Float('Feed cost cow day',
                                     compute='_get_lot_calcs', readonly=True)
    diff_ing_cost = fields.Float('Diff ing cost', compute='_get_lot_calcs',
                                 readonly=True)
    perc_feed_milk_ingress = fields.Float('Perc feed milk ingress',
                                          compute='_get_lot_calcs',
                                          readonly=True)
    perc_purchased_feed_milk_ingress = fields.Float(
        'Perc purchased feed milk ingress', compute='_get_lot_calcs',
        readonly=True)
    perc_concentrated_milk_ingress = fields.Float(
        'Perc concentrated milk ingress', compute='_get_lot_calcs',
        readonly=True)
    liters_produced_kg_concentrated_used = fields.Float(
        'Liters produced kg concentrated used', compute='_get_lot_calcs',
        readonly=True)
    lot_threshold_point_slaughterhouse = fields.Float(
        'Lot threshold point slaughterhouse', compute='_get_lot_calcs',
        readonly=True)
    lot_threshold_point_dry = fields.Float('Lot threshold point dry',
                                           compute='_get_lot_calcs',
                                           readonly=True)
    milk_cow_production = fields.Float('', compute='_get_lot_calcs',
                                       readonly=True)
    milk_cow_production_corrected = fields.Float('', compute='_get_lot_calcs',
                                                 readonly=True)
    eat_cow_production = fields.Float('', compute='_get_lot_calcs',
                                      readonly=True)
    eat_cow_production_corrected = fields.Float('', compute='_get_lot_calcs',
                                                readonly=True)
    cubicle_production = fields.Float('', compute='_get_lot_calcs',
                                      readonly=True)
    cubicle_production_corrected = fields.Float('', compute='_get_lot_calcs',
                                                readonly=True)
    sequence_id = fields.Many2one('lot.detail.sequence', 'Sequence')
    sequence = fields.Integer('Sequence', related='sequence_id.name')
    max_seq = fields.Integer('', compute='_get_max_sequence', store=True)

    total_theo_kg = fields.Float('Total Kg theorical', compute='_get_lot_calcs')
    total_theo_ms = fields.Float('', compute='_get_lot_calcs')
    total_theo_enl = fields.Float('Total ENL theorical', compute='_get_lot_calcs')
    total_theo_pb = fields.Float('Total PB theorical', compute='_get_lot_calcs')

    total_kg = fields.Float('Total Kg', compute='_get_lot_calcs')
    total_ms = fields.Float('', compute='_get_lot_calcs')
    total_enl = fields.Float('Total ENL', compute='_get_lot_calcs')
    total_pb = fields.Float('Total PB', compute='_get_lot_calcs')

    @api.multi
    def _set_kf_mf_carriage(self):
        for lot_detail in self:
            if sum([x.kg_ration for x in lot_detail.lot_contents]) > 0:
                lot_detail.rations_make_number = float(lot_detail.kf_mf_carriage) / sum([x.kg_ration for x in lot_detail.lot_contents])

    @api.multi
    @api.depends('rations_make_number', 'lot_contents.kg_ration')
    def _get_kf_mf_carraige(self):
        for lot_detail in self:
            lot_detail.kf_mf_carriage = lot_detail.rations_make_number * sum([x.kg_ration for x in lot_detail.lot_contents])

    @api.depends('lot_id.farm_id.farm_lots', 'user_id')
    def _get_max_sequence(self):
        for detail in self:
            lot_partner = self.env['lot.partner'].search(
                [('farm_id', '=', detail.lot_id.farm_id.id),
                 ('year_id.date_start', '<=', detail.lot_id.date),
                 ('year_id.date_stop', '>=', detail.lot_id.date)])
            detail.max_seq = lot_partner and lot_partner[0].lot_number or 0

    _sql_constraints = [
        ('uniq_sequence_per_lot', 'unique (sequence_id, lot_id)',
         'The sequence must be unique !')
    ]

    @api.multi
    @api.depends('perc_ms_ration_anal')
    def _get_lot_calcs(self):
        for lot_detail in self:
            lot = lot_detail.lot_id
            res = {}
            total_theo_kg_ration = sum([x.theorical_kg_ration for x in
                                        lot_detail.lot_contents])
            total_kg_ration = sum([x.kg_ration for x in
                                   lot_detail.lot_contents])
            res['kg_mf_ration_theo'] = total_theo_kg_ration
            res['kg_mf_ration_real'] = total_kg_ration
            res['kg_mf_ration_anal'] = total_kg_ration
            if total_theo_kg_ration != 0.0:
                res['perc_ms_ration_theo'] = sum(
                    [x.theorical_kg_ration * x.theorical_ms for x in
                     lot_detail.lot_contents]) / total_theo_kg_ration
            else:
                res['perc_ms_ration_theo'] = 0.0
            if total_kg_ration != 0.0:
                res['perc_ms_ration_real'] = sum([x.kg_ration * x.ms for x in
                                                  lot_detail.lot_contents]) / \
                    total_kg_ration
            else:
                res['perc_ms_ration_real'] = 0.0
            res['kg_ms_ration_theo'] = res['kg_mf_ration_theo'] * \
                (res['perc_ms_ration_theo'] / 100.0)
            res['kg_ms_ration_real'] = res['kg_mf_ration_real'] * \
                (res['perc_ms_ration_real'] / 100.0)
            res['kg_ms_ration_anal'] = res['kg_mf_ration_anal'] * \
                (lot_detail.perc_ms_ration_anal / 100.0)
            if lot_detail.number_milking_cows + \
                    ((lot_detail.cows_eat_number - lot_detail.number_milking_cows)
                     / 2) != 0:
                res['imf_theo'] = (
                    (lot_detail.rations_make_number * total_theo_kg_ration) -
                    float(lot_detail.surplus)) / \
                    (lot_detail.number_milking_cows + ((lot_detail.cows_eat_number -
                                                 lot_detail.number_milking_cows) / 2))
            else:
                res['imf_theo'] = 0.0
            if (lot_detail.number_milking_cows +
                ((lot_detail.cows_eat_number - lot_detail.number_milking_cows) /
                 2)) != 0:
                res['imf_real'] = (lot_detail.kf_mf_carriage -
                                   float(lot_detail.surplus)) / \
                    (lot_detail.number_milking_cows + ((lot_detail.cows_eat_number -
                                                lot_detail.number_milking_cows) / 2))
            else:
                res['imf_real'] = 0

            res['total_theo_kg'] = sum([x.theorical_kg_ration for x in lot_detail.lot_contents])
            if res['total_theo_kg'] != 0:
                res['total_theo_ms'] = sum([x.theorical_ms * x.theorical_kg_ration for x in lot_detail.lot_contents]) / res['total_theo_kg']
            else:
                res['total_theo_ms'] = 0
            if sum([x.theorical_kg_ration * x.theorical_ms for x in lot_detail.lot_contents]) != 0:
                res['total_theo_enl'] = sum(
                    [(x.theorical_kg_ration * x.theorical_ms) * x.theorical_enl
                     for x in lot_detail.lot_contents]) / \
                     sum([x.theorical_kg_ration * x.theorical_ms
                          for x in lot_detail.lot_contents])
            else:
                res['total_theo_enl'] = 0

            if sum([x.theorical_kg_ration * x.theorical_ms for x in lot_detail.lot_contents]) != 0:
                res['total_theo_pb'] = (
                    sum([(x.theorical_kg_ration * x.theorical_ms) * x.theorical_pb * 1000
                         for x in lot_detail.lot_contents]) /
                        sum([x.theorical_kg_ration * x.theorical_ms
                             for x in lot_detail.lot_contents])) / 1000
            else:
                res['total_theo_pb'] = 0

            res['total_kg'] = sum([x.kg_ration for x in lot_detail.lot_contents])
            if res['total_kg'] != 0:
                res['total_ms'] = sum([x.ms * x.kg_ration for x in lot_detail.lot_contents]) / res['total_kg']
            else:
                res['total_ms'] = 0
            if sum([x.kg_ration * x.ms for x in lot_detail.lot_contents]) != 0:
                res['total_enl'] = sum(
                    [(x.kg_ration * x.ms) * x.enl
                     for x in lot_detail.lot_contents]) / \
                     sum([x.kg_ration * x.ms
                          for x in lot_detail.lot_contents])
            else:
                res['total_enl'] = 0

            if sum([x.kg_ration * x.ms for x in lot_detail.lot_contents]) != 0:
                res['total_pb'] = (
                    sum([(x.kg_ration * x.ms) * x.pb * 1000
                         for x in lot_detail.lot_contents]) /
                        sum([x.kg_ration * x.ms
                             for x in lot_detail.lot_contents])) / 1000
            else:
                res['total_pb'] = 0

            res['imf_anal'] = res['imf_real']
            if lot_detail.cows_eat_number:
                res['kg_plucking_cow_day_theo'] = lot_detail.kg_plucking_theo / lot_detail.cows_eat_number
                res['kg_plucking_cow_day_real'] = res['kg_plucking_cow_day_anal'] = lot_detail.kg_plucking / lot_detail.cows_eat_number
                res['ims_plucking_kg_cow_day_theo'] = res['ims_plucking_kg_cow_day_real'] = res['ims_plucking_kg_cow_day_anal'] = lot_detail.kg_plucking_theo * (lot_detail.ms_plucking / 100) / lot_detail.cows_eat_number

            else:
                res['kg_plucking_cow_day_theo'] =  res['kg_plucking_cow_day_real'] = res['kg_plucking_cow_day_anal'] = 0
                res['ims_plucking_kg_cow_day_theo'] = res['ims_plucking_kg_cow_day_real'] = res['ims_plucking_kg_cow_day_anal'] = 0

            if res['imf_theo'] != 0:
                res['ims_total_kg_cow_day_theo'] = \
                    res['perc_ms_ration_theo'] / 100 * res['imf_theo']
            else:
                res['ims_total_kg_cow_day_theo'] = 0
            if res['imf_real'] != 0:
                res['ims_total_kg_cow_day_real'] = \
                    res['perc_ms_ration_real'] / 100 * res['imf_real']
            else:
                res['ims_total_kg_cow_day_real'] = 0
            if res['imf_anal'] != 0:
                res['ims_total_kg_cow_day_anal'] = \
                    lot_detail.perc_ms_ration_anal / 100 * res['imf_anal']
            else:
                res['ims_total_kg_cow_day_anal'] = 0
            res['ims_unifed_kg_cow_day_theo'] = res['ims_total_kg_cow_day_theo'] - res['ims_plucking_kg_cow_day_theo']
            res['ims_unifed_kg_cow_day_real'] = res['ims_total_kg_cow_day_real'] - res['ims_plucking_kg_cow_day_real']
            res['ims_unifed_kg_cow_day_anal'] = res['ims_total_kg_cow_day_anal'] - res['ims_plucking_kg_cow_day_anal']

            if lot_detail.number_milking_cows != 0:
                res['milk_cow_production'] = (
                    float(lot_detail.tank_liters) + lot_detail.retired_liters +
                    lot_detail.liters_on_farm_consumption) / \
                    lot_detail.number_milking_cows
            else:
                res['milk_cow_production'] = 0
            if lot_detail.cows_eat_number != 0:
                res['eat_cow_production'] = (
                    float(lot_detail.tank_liters) + lot_detail.retired_liters +
                    lot_detail.liters_on_farm_consumption) / \
                    lot_detail.cows_eat_number
            else:
                res['eat_cow_production'] = 0

            if res['ims_total_kg_cow_day_theo'] != 0:
                res['ic_liters_kg_theo'] = res['milk_cow_production'] / \
                    res['ims_total_kg_cow_day_theo']
            else:
                res['ic_liters_kg_theo'] = 0
            if res['ims_total_kg_cow_day_real'] != 0:
                res['ic_liters_kg_real'] = res['milk_cow_production'] / \
                    res['ims_total_kg_cow_day_real']
            else:
                res['ic_liters_kg_real'] = 0
            if res['ims_total_kg_cow_day_anal'] != 0:
                res['ic_liters_kg_anal'] = res['milk_cow_production'] / \
                    res['ims_total_kg_cow_day_anal']
            else:
                res['ic_liters_kg_anal'] = 0

            res['milk_cow_production_corrected'] = (
                12.82 * res['milk_cow_production'] * (lot.mg / 100)) + \
                (7.13 * res['milk_cow_production'] *
                 (lot.mp / 100) + (0.323 * res['milk_cow_production']))
            res['eat_cow_production_corrected'] = (
                12.82 * res['eat_cow_production'] * (lot.mg / 100)) + \
                (7.13 * res['eat_cow_production'] * (lot.mp / 100) +
                 (0.323 * res['eat_cow_production']))

            if res['ims_total_kg_cow_day_theo'] != 0:
                res['ic_corrected_liters_kg_theo'] = \
                    res['milk_cow_production_corrected'] / \
                    res['ims_total_kg_cow_day_theo']
            else:
                res['ic_corrected_liters_kg_theo'] = 0
            if res['ims_total_kg_cow_day_real'] != 0:
                res['ic_corrected_liters_kg_real'] = \
                    res['milk_cow_production_corrected'] / \
                    res['ims_total_kg_cow_day_real']
            else:
                res['ic_corrected_liters_kg_real'] = 0
            if res['ims_total_kg_cow_day_anal'] != 0:
                res['ic_corrected_liters_kg_anal'] = \
                    res['milk_cow_production_corrected'] / \
                    res['ims_total_kg_cow_day_anal']
            else:
                res['ic_corrected_liters_kg_anal'] = 0

            r35 = sum([x.theorical_kg_ration * (x.theorical_ms / 100.0) *
                       x.theorical_enl for x in lot_detail.lot_contents])
            q35 = sum([x.theorical_kg_ration * (x.theorical_ms / 100.0)
                       for x in lot_detail.lot_contents])
            if q35 != 0:
                func = '((%s * r35 / q35)-(0.08 * lot.live_weight ** 0.75))\
/ ((0.0929 * lot.mg) + (0.0547 * lot.mp)+(0.0395 * 4.85))'
                res['milk_prediction_by_enl_theo'] = eval(
                    func % res['ims_total_kg_cow_day_theo'])
                res['milk_prediction_by_enl_real'] = eval(
                    func % res['ims_total_kg_cow_day_real'])
                res['milk_prediction_by_enl_anal'] = eval(
                    func % res['ims_total_kg_cow_day_anal'])
            else:
                res['milk_prediction_by_enl_theo'] = res['milk_prediction_by_enl_real'] = res['milk_prediction_by_enl_anal'] = 0.0

            s35 = sum([x.theorical_kg_ration * (x.theorical_ms / 100.0) *
                       (x.theorical_pb / 100.0) * 1000 for x in
                       lot_detail.lot_contents])
            if q35 != 0:
                s36 = s35 / q35
            else:
                s36 = 0
            res['milk_prediction_by_pb_theo'] = (
                (res['ims_total_kg_cow_day_theo'] * s36)-450) / 86
            res['milk_prediction_by_pb_real'] = (
                (res['ims_total_kg_cow_day_real'] * s36)-450) / 86
            res['milk_prediction_by_pb_anal'] = (
                (res['ims_total_kg_cow_day_anal'] * s36)-450) / 86

            res['real_production_deviation_theo'] = res['milk_prediction_by_enl_theo'] < res['milk_prediction_by_pb_theo'] and res['milk_cow_production_corrected'] - res['milk_prediction_by_enl_theo'] or res['milk_cow_production_corrected'] - res['milk_prediction_by_pb_theo']
            res['real_production_deviation_real'] = res['milk_prediction_by_enl_real'] < res['milk_prediction_by_pb_real'] and res['milk_cow_production_corrected'] - res['milk_prediction_by_enl_real'] or res['milk_cow_production_corrected'] - res['milk_prediction_by_pb_real']
            res['real_production_deviation_anal'] = res['milk_prediction_by_enl_anal'] < res['milk_prediction_by_pb_anal'] and res['milk_cow_production_corrected'] - res['milk_prediction_by_enl_anal'] or res['milk_cow_production_corrected'] - res['milk_prediction_by_pb_anal']

            res['ration_cost_eur_theo'] = sum(
                [x.theorical_kg_ration * x.eur_ton_mf /
                 1000 for x in lot_detail.lot_contents])
            res['ration_cost_eur_anal'] = res['ration_cost_eur_real'] = sum([x.kg_ration * x.eur_ton_mf / 1000 for x in lot_detail.lot_contents])

            if total_theo_kg_ration != 0:
                res['ration_cost_eur_ton_mf_theo'] = res['ration_cost_eur_theo'] / total_theo_kg_ration * 1000
            else:
                res['ration_cost_eur_ton_mf_theo'] = 0.0
            if total_kg_ration != 0:
                res['ration_cost_eur_ton_mf_real'] = res['ration_cost_eur_real'] / total_kg_ration * 1000
            else:
                res['ration_cost_eur_ton_mf_real'] = 0.0
            if total_kg_ration != 0:
                res['ration_cost_eur_ton_mf_anal'] = res['ration_cost_eur_anal'] / total_kg_ration * 1000
            else:
                res['ration_cost_eur_ton_mf_anal'] = 0.0

            if res['perc_ms_ration_theo'] != 0:
                res['ration_cost_eur_ton_ms_theo'] = res['ration_cost_eur_ton_mf_theo'] / (res['perc_ms_ration_theo'] / 100.0)
            else:
                res['ration_cost_eur_ton_ms_theo'] = 0.0
            if res['perc_ms_ration_real'] != 0:
                res['ration_cost_eur_ton_ms_real'] = res['ration_cost_eur_ton_mf_real'] / (res['perc_ms_ration_real'] / 100.0)
            else:
                res['ration_cost_eur_ton_ms_real'] = 0.0
            if lot_detail.perc_ms_ration_anal != 0:
                res['ration_cost_eur_ton_ms_anal'] = res['ration_cost_eur_ton_mf_anal'] / (lot_detail.perc_ms_ration_anal / 100.0)
            else:
                res['ration_cost_eur_ton_ms_anal'] = 0.0

            res['ration_carriage_cost_eur_cow_day_theo'] = (res['ims_total_kg_cow_day_theo'] * res['ration_cost_eur_ton_ms_theo'] / 1000) + lot.carriage_cost_cow_day
            res['ration_carriage_cost_eur_cow_day_real'] = (res['ims_total_kg_cow_day_real'] * res['ration_cost_eur_ton_ms_real'] / 1000) + lot.carriage_cost_cow_day
            res['ration_carriage_cost_eur_cow_day_anal'] = (res['ims_total_kg_cow_day_anal'] * res['ration_cost_eur_ton_ms_anal'] / 1000) + lot.carriage_cost_cow_day

            if res['milk_cow_production'] != 0:
                res['ration_carriage_cost_eur_liter_theo'] = (res['ration_carriage_cost_eur_cow_day_theo'] / res['milk_cow_production']) * 100
                res['ration_carriage_cost_eur_liter_real'] = (res['ration_carriage_cost_eur_cow_day_real'] / res['milk_cow_production']) * 100
                res['ration_carriage_cost_eur_liter_anal'] = (res['ration_carriage_cost_eur_cow_day_anal'] / res['milk_cow_production']) * 100
                if res['milk_cow_production_corrected'] != 0:
                    res['ration_carriage_cost_corrected_milk_eur_liter_theo'] = (res['ration_carriage_cost_eur_cow_day_theo'] / res['milk_cow_production_corrected']) * 100
                    res['ration_carriage_cost_corrected_milk_eur_liter_real'] = (res['ration_carriage_cost_eur_cow_day_real'] / res['milk_cow_production_corrected']) * 100
                    res['ration_carriage_cost_corrected_milk_eur_liter_anal'] = (res['ration_carriage_cost_eur_cow_day_anal'] / res['milk_cow_production_corrected']) * 100
                else:
                    res['ration_carriage_cost_corrected_milk_eur_liter_theo'] = res['ration_carriage_cost_corrected_milk_eur_liter_real'] = res['ration_carriage_cost_corrected_milk_eur_liter_theo'] = 0.0
            else:
                res['ration_carriage_cost_eur_liter_theo'] = res['ration_carriage_cost_eur_liter_real'] = res['ration_carriage_cost_eur_liter_anal'] = 0.0
                res['ration_carriage_cost_corrected_milk_eur_liter_theo'] = res['ration_carriage_cost_corrected_milk_eur_liter_real'] = res['ration_carriage_cost_corrected_milk_eur_liter_theo'] = 0.0

            res['grs_fat_cow_day'] = res['milk_cow_production'] * lot.mg * 10
            res['grs_protein_cow_day'] = res['milk_cow_production'] * \
                lot.mp * 10

            if lot_detail.number_milking_cows != 0:
                res['ingress_milk_cow_day'] = (float(lot_detail.tank_liters) /
                                               lot_detail.number_milking_cows) * \
                    lot.milk_price / 1000
            else:
                res['ingress_milk_cow_day'] = 0
            res['feed_cost_cow_day'] = \
                res['ration_carriage_cost_eur_cow_day_real']
            res['diff_ing_cost'] = res['ingress_milk_cow_day'] - \
                res['feed_cost_cow_day']

            if res['ingress_milk_cow_day'] != 0:
                res['perc_feed_milk_ingress'] = res['feed_cost_cow_day'] / \
                    res['ingress_milk_cow_day'] * 100

                total_kg_ration_purchased = sum([x.kg_ration for x in lot_detail.lot_contents if x.purchase])
                if total_kg_ration_purchased != 0.0:
                    perc_ms_ration_real_purchased = sum([x.kg_ration * x.ms for x in
                                                      lot_detail.lot_contents if x.purchase]) / total_kg_ration_purchased
                else:
                    perc_ms_ration_real_purchased = 0.0
                if res['imf_real'] != 0:
                    ims_total_kg_cow_day_real_purchased = perc_ms_ration_real_purchased / 100 * res['imf_real']
                else:
                    ims_total_kg_cow_day_real_purchased = 0
                feed_cost_cow_day_purchased = (ims_total_kg_cow_day_real_purchased * res['ration_cost_eur_ton_ms_real'] / 1000) + lot.carriage_cost_cow_day
                res['perc_purchased_feed_milk_ingress'] = feed_cost_cow_day_purchased / res['ingress_milk_cow_day'] * 100
            else:
                res['perc_feed_milk_ingress'] = 0.0
                res['perc_purchased_feed_milk_ingress'] = 0.0

            y3 = sum([x.kg_ration * x.eur_ton_mf / 1000 for x in
                      lot_detail.lot_contents if x.product_id.concentrated])
            if res['ingress_milk_cow_day'] != 0 and lot_detail.cows_eat_number:
                res['perc_concentrated_milk_ingress'] = (
                    (y3 * lot_detail.rations_make_number) /
                    lot_detail.cows_eat_number /
                    res['ingress_milk_cow_day']) * 100
            else:
                res['perc_concentrated_milk_ingress'] = 0.0
            i3 = sum([x.kg_ration for x in lot_detail.lot_contents
                      if x.product_id.concentrated])
            if i3 * lot_detail.rations_make_number != 0:
                res['liters_produced_kg_concentrated_used'] = (
                    float(lot_detail.tank_liters) + lot_detail.retired_liters +
                    lot_detail.liters_on_farm_consumption) / \
                    (i3 * lot_detail.rations_make_number)
            else:
                res['liters_produced_kg_concentrated_used'] = 0.0

            if lot_detail.number_cubicles_in_lot:
                res['cubicle_production'] = \
                    (lot_detail.tank_liters +
                     lot_detail.liters_on_farm_consumption +
                     lot_detail.retired_liters) / \
                     lot_detail.number_cubicles_in_lot
                res['cubicle_production_corrected'] = \
                    (12.82 * res['cubicle_production'] * (lot.mg / 100.0)) + \
                    (7.13 * res['cubicle_production'] * (lot.mp / 100.0) + \
                    (0.323 * res['cubicle_production']))
            else:
                res['cubicle_production'] = 0.0
                res['cubicle_production_corrected'] = 0.0

            if lot.milk_price != 0.0:
                res['lot_threshold_point_slaughterhouse'] = \
                    res['ration_carriage_cost_eur_cow_day_real'] / \
                    (lot.milk_price / 1000)
                res['lot_threshold_point_dry'] = (
                    res['ration_carriage_cost_eur_cow_day_real'] -
                    lot.dry_cow_ration_cost) / (lot.milk_price / 1000)
            else:
                res['lot_threshold_point_slaughterhouse'] = 0.0
                res['lot_threshold_point_dry'] = 0.0

            for field in res.keys():
                lot_detail[field] = res[field]


class LotContent(models.Model):

    _name = 'lot.content'

    detail_id = fields.Many2one('lot.detail', 'Detail')
    eur_ton_mf = fields.Integer('€/Tn MF')
    product_id = fields.Many2one('product.product', 'Product', required=True,
                                 domain=[('ingredient', '=', True)])
    kg_ration = fields.Float('Kg/Ration')
    ms = fields.Float('%MS', digits=(12, 2))
    enl = fields.Float('ENL', digits=(12, 2))
    pb = fields.Float('%PB', digits=(12, 2))
    theorical_kg_ration = fields.Float('Kg/Ration', digits=(12, 2))
    theorical_ms = fields.Float('%MS', digits=(12, 2))
    theorical_enl = fields.Float('ENL', digits=(12, 2))
    theorical_pb = fields.Float('%PB', digits=(12, 2))
    message_kg = fields.Char(compute='_compute_message')
    message_ms = fields.Char(compute='_compute_message')
    message_enl = fields.Char(compute='_compute_message')
    message_pb = fields.Char(compute='_compute_message')
    purchase = fields.Boolean()

    @api.multi
    def set_real_by_theorical(self):
        for content in self:
            content.kg_ration = content.theorical_kg_ration
            content.ms = content.theorical_ms
            content.enl = content.theorical_enl
            content.pb = content.theorical_pb

    @api.depends('kg_ration', 'ms', 'enl', 'pb', 'theorical_kg_ration',
                 'theorical_ms', 'theorical_enl', 'theorical_pb')
    def _compute_message(self):
        for content in self:
            if content.kg_ration != content.theorical_kg_ration:
                content.message_kg = 'Cantidades diferentes'
            else:
                content.message_kg = ''
            if content.ms != content.theorical_ms:
                content.message_ms = 'Cantidades diferentes'
            else:
                content.message_kg = ''
            if content.enl != content.theorical_enl:
                content.message_enl = 'Cantidades diferentes'
            else:
                content.message_kg = ''
            if content.pb != content.theorical_pb:
                content.message_pb = 'Cantidades diferentes'
            else:
                content.message_kg = ''

    @api.onchange('product_id', 'detail_id')
    def onchange_product_id(self):
        for content in self:
            if not content.product_id:
                continue
            last_lot = self.env['lot'].search(
                [('farm_id', '=', self._context['farm']),
                 ('id', '!=', self._context['lot_id']),
                 ('date', '<=', self._context['lot_date'])],
                order='date desc', limit=1)
            if last_lot:
                detail = self.env['lot.detail'].search(
                    [('lot_id', '=', last_lot.id),
                     ('sequence', '=', content.detail_id.sequence)], limit=1)
                if detail:
                    last_content = self.env['lot.content'].search(
                        [('detail_id', '=', detail.id),
                         ('product_id', '=', content.product_id.id)])
                    if last_content:
                        content['theorical_kg_ration'] = last_content.kg_ration
                        content['theorical_ms'] = last_content.ms
                        content['theorical_enl'] = last_content.enl
                        content['theorical_pb'] = last_content.pb
