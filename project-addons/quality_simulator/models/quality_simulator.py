# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class QualitySimulator(models.Model):
    _name = 'quality.simulator'
    _rec_name = 'date'

    exploitation = fields.Many2one(
        'res.partner', 'Exploitation', required=True,
        default=lambda self: self.env.user.company_id.partner_id.id)
    date = fields.Date()
    pay_fat = fields.Float('Pay fat (€/dec)', digits=(4, 4))
    pay_protein = fields.Float('Pay protein (€/dec)', digits=(4, 4))
    milk_price_now = fields.Float('Milk price (€/l)', digits=(4, 4))
    fat_percentage_now = fields.Float('% Fat', digits=(4, 4))
    protein_percentage_now = fields.Float('% Protein', digits=(4, 4))
    lactose_percentage_now = fields.Float('% lactose', digits=(4, 4),
                                          default=4.85)
    liters_now = fields.Float('Liters', digits=(4, 4))
    entry_now = fields.Float('Entry', readonly=True, compute='_get_calc_vals',
                             digits=(4, 4))
    ration_cost_now = fields.Float('Actual ration cost (€/cow and day)',
                                   digits=(4, 4))
    benefit_now = fields.Float('Benefit', readonly=True,
                               compute='_get_calc_vals', digits=(4, 4))
    milk_price_future = fields.Float('Milk price (€/l)', readonly=True,
                                     compute='_get_calc_vals', digits=(4, 4))
    fat_percentage_future = fields.Float('% Fat', digits=(4, 4))
    protein_percentage_future = fields.Float('% Protein', digits=(4, 4))
    lactose_percentage_future = fields.Float('% lactose', digits=(4, 4),
                                             default=4.85)
    liters_future = fields.Float('Liters', readonly=True,
                                 compute='_get_calc_vals', digits=(4, 4))
    entry_future = fields.Float('Entry', readonly=True,
                                compute='_get_calc_vals', digits=(4, 4))
    ration_cost_future = fields.Float('Future ration cost (€/cow and day)',
                                      readonly=True, compute='_get_calc_vals',
                                      digits=(4, 4))
    benefit_future = fields.Float('Benefit', readonly=True,
                                  compute='_get_calc_vals', digits=(4, 4))

    cow_liveweight = fields.Float()
    ration_overrun = fields.Float()

    production_increase = fields.Float(readonly=True, compute='_get_calc_vals')
    profit_increase = fields.Float(readonly=True, compute='_get_calc_vals')

    @api.multi
    def _get_calc_vals(self):
        for simulator in self:
            simulator.entry_now = simulator.milk_price_now * \
                simulator.liters_now
            simulator.benefit_now = simulator.entry_now - \
                simulator.ration_cost_now
            simulator.milk_price_future = simulator.milk_price_now + (
                (simulator.fat_percentage_future -
                 simulator.fat_percentage_now) *
                simulator.pay_fat * 10) + \
                ((simulator.protein_percentage_future -
                  simulator.protein_percentage_now) *
                 simulator.pay_protein * 10)
            simulator.ration_cost_future = simulator.ration_cost_now + \
                simulator.ration_overrun
            if simulator.milk_price_now:
                simulator.liters_future = (simulator.ration_cost_future +
                                           simulator.benefit_now) / \
                    simulator.milk_price_now
            simulator.entry_future = simulator.milk_price_future * \
                simulator.liters_future
            simulator.benefit_future = simulator.entry_future - \
                simulator.ration_cost_future

            enl_now = simulator.liters_now * \
                ((0.0929 * simulator.fat_percentage_now) +
                 (0.0547 * simulator.protein_percentage_now) +
                 (0.0395 * simulator.lactose_percentage_now))

            enl_future = simulator.liters_future * \
                ((0.0929 * simulator.fat_percentage_future) +
                 (0.0547 * simulator.protein_percentage_future) +
                 (0.0395 * simulator.lactose_percentage_future))

            enl_diff = enl_now - enl_future

            en_cost = (0.0929 * simulator.fat_percentage_future) + \
                      (0.0547 * simulator.protein_percentage_future) + \
                      (0.0395 * simulator.lactose_percentage_future)

            simulator.production_increase = enl_diff / en_cost

            simulator.profit_increase = simulator.production_increase * \
                simulator.milk_price_future
