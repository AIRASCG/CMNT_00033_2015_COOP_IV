# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from openerp import models, fields, api


class FarmNotebook(models.Model):

    _name = 'farm.notebook'

    partner = fields.Many2one('res.partner')
    date = fields.Date()
    phytosanitary_applicators = fields.One2many(
        'phytosanitary.applicator.notebook', 'notebook')
    phytosanitary_machines = fields.One2many(
        'phytosanitary.machine.notebook', 'notebook')
    advisor_entity = fields.One2many('advisor.entity', 'notebook')
    partner_fields = fields.One2many('res.partner.fields.notebook', 'notebook')
    phytosanitary_uses = fields.One2many('phytosanitary.use.notebook', 'notebook')
    phytosanitary_advised_uses = fields.One2many('phytosanitary.advised.use.notebook', 'notebook')
    apply_seeds_treatement = fields.Boolean()
    treated_seed_uses = fields.One2many('treated.seed.use.notebook', 'notebook')
    apply_post_harvest_treatement = fields.Boolean()
    post_harvest_treatements = fields.One2many('post.harvest.treatements.notebook', 'notebook')

    apply_storage_treatement = fields.Boolean()
    storage_tratements = fields.One2many('storage.treatements.notebook', 'notebook')

    apply_transport_treatement = fields.Boolean()
    transport_tratements = fields.One2many('transport.treatements.notebook', 'notebook')
    solded_harvests = fields.One2many('solded.harvest', 'notebook')

    @api.multi
    def get_notebook_data(self):
        cooperative = self.partner.company_id.cooperative_company
        notebook_year = datetime.strptime(self.date, '%Y-%m-%d').year
        write_vals = {'advisor_entity': [(0, 0, {'name': cooperative.name, 'vat': cooperative.vat})]}
        phyto_uses = self.env['phytosanitary.use'].search([('phytosanitary.company_id', '=', self.partner.company_id.id), ('date', '>=', '%s-01-01' % notebook_year), ('date', '<=', '%s-12-31' % notebook_year)])
        applicators = []
        applicators_sequence = 0
        machines = []
        machines_sequence = 0
        for use in phyto_uses:
            if use.applicator.id not in [x[2]['applicator'] for x in applicators]:
                applicators_sequence += 1
                applicators_data = use.applicator.copy_data()[0]
                import ipdb; ipdb.set_trace()
                applicators_data['applicator'] = use.applicator.id
                applicators_data['sequence'] = applicators_sequence
                applicators.append((0, 0, applicators_data))
            if use.machine.id not in [x[2]['machine'] for x in machines]:
                machines_sequence += 1
                machines_data = use.applicator.copy_data()[0]
                machines_data['machine'] = use.machine.id
                machines_data['sequence'] = machines_sequence
                machines.append((0, 0, machines_data))
        write_vals['phytosanitary_applicators'] = applicators
        write_vals['phytosanitary_machines'] = machines
        partner_fields = self.env['res.partner.fields'].search([('year', '=', notebook_year), ('partner_id', '=', self.partner.id)])
        partner_fieds_dict = []
        field_sequence = 0
        for field in partner_fields:
            field_sequence += 1
            field_data = field.copy_data()[0]
            field_data['sequence'] = field_sequence
            partner_fieds_dict.append((0, 0, field_data))
        write_vals['partner_fields'] = partner_fieds_dict

        self.write(write_vals)



class PhytosanitaryApplicatorNotebook(models.Model):

    _name = 'phytosanitary.applicator.notebook'
    _inherit = ['phytosanitary.applicator']

    applicator = fields.Many2one('phytosanitary.applicator')
    sequence = fields.Integer()
    notebook = fields.Many2one('farm.notebook')


class PhytosanitaryMachineNotebook(models.Model):

    _name = 'phytosanitary.machine.notebook'
    _inherit = ['phytosanitary.machine']

    machine = fields.Many2one('phytosanitary.machine')
    sequence = fields.Integer()
    notebook = fields.Many2one('farm.notebook')


class AdvisorEntity(models.Model):

    _name = 'advisor.entity'

    notebook = fields.Many2one('farm.notebook')
    name = fields.Char()
    vat = fields.Char()
    id_number = fields.Char()
    farm_type = fields.Char()


class ResPartnerFieldsNotebook(models.Model):

    _name = 'res.partner.fields.notebook'
    _inherit = ['res.partner.fields']

    sequence = fields.Integer()
    notebook = fields.Many2one('farm.notebook')


class PhytosanitaryUseNotebook(models.Model):

    _name = 'phytosanitary.use.notebook'

    field = fields.Many2one('res.partner.fields.notebook')
    applicator = fields.Many2one('phytosanitary.applicator.notebook')
    machine = fields.Many2one('phytosanitary.machine.notebook')
    notebook = fields.Many2one('farm.notebook')


class PhytosanitaryAdvisedUseNotebook(models.Model):

    _name = 'phytosanitary.advised.use.notebook'
    notebook = fields.Many2one('farm.notebook')


class TreatedSeedUse(models.Model):

    _name = 'treated.seed.use.notebook'
    notebook = fields.Many2one('farm.notebook')
    date = fields.Date()
    field = fields.Many2one('res.partner.fields.notebook')
    cultivation_specie = fields.Char()
    cultivation_variety = fields.Char()
    seeded_surface = fields.Float()
    seed_quantity = fields.Float()
    phytosanitary_name = fields.Char()
    phytosanitary_registry_number = fields.Char()


class PostHarvestTreatements(models.Model):

    _name = 'post.harvest.treatements.notebook'
    notebook = fields.Many2one('farm.notebook')
    date = fields.Date()
    vegetable_product_treated = fields.Char()
    phytosanitary_problem = fields.Char()
    treated_qty = fields.Float()
    phytosanitary_name = fields.Char()
    phytosanitary_registry_number = fields.Char()
    used_qty = fields.Char()
    used_uom = fields.Many2one('product.uom')


class StorageTreatements(models.Model):

    _name = 'storage.treatements.notebook'
    notebook = fields.Many2one('farm.notebook')


class TransportTreatements(models.Model):

    _name = 'transport.treatements.notebook'
    notebook = fields.Many2one('farm.notebook')


class SoldedHarvest(models.Model):

    _name = 'solded.harvest'
    notebook = fields.Many2one('farm.notebook')
