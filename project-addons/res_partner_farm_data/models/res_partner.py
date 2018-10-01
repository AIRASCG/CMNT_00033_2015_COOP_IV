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
from openerp import tools
from openerp import models, fields, api, exceptions, _
from datetime import datetime, date
import time


class ProductSurfaceByPartner(models.Model):

    _name = 'product.surface.by.partner'
    _auto = False
    _order = 'year desc,product_id desc'

    product_id = fields.Many2one('res.partner.fields.product', 'Product')
    partner_id = fields.Many2one('res.partner')
    surface = fields.Float()
    year = fields.Char("Año")

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'product_surface_by_partner')
        cr.execute("""
            CREATE VIEW product_surface_by_partner as (
                SELECT row_number() over () AS id,
                       product_id,
                       partner_id,
                       year,
                       SUM(surface) AS surface
                FROM (
                        SELECT product_1 AS product_id,
                               partner_id,
                               SUM(net_surface) AS surface, year
                        FROM res_partner_fields
                        GROUP BY product_1, partner_id, year

                        UNION

                        SELECT product_2 AS product_id,
                               partner_id,
                               SUM(net_surface) AS surface, year
                        FROM res_partner_fields
                        GROUP BY product_2, partner_id, year) AS x
                GROUP BY product_id, partner_id, year
            );
        """)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    latitude = fields.Char()
    longitude = fields.Char()
    gescarro_reference = fields.Char()
    erp_reference = fields.Char()
    farm = fields.Boolean('Farm')
    temporary_farm = fields.Boolean(
        'Temporary farm', readonly=True,
        related='company_id.not_configured_accounting')
    temporary = fields.Boolean('Temporary',  related='company_id.temporary')
    is_cooperative = fields.Boolean(
        'Cooperative', readonly=True, related='company_id.is_cooperative')
    partner_of = fields.Char('Partner of')
    exploitation_technician = fields.Many2one('res.users',
                                              'Exploitation technician')
    secondary_technician = fields.Many2one('res.users', 'Secondary technician')
    barn_type = fields.Selection((('free', 'Free'), ('stuck', 'Stuck'),
                                  ('mixed', 'Mixed')), 'Barn type')
    dairy_company = fields.Many2one('res.partner', 'Dairy company')
    bed_suppliers = fields.Many2many('res.partner', 'farm_bed_supplier_rel',
                                     'farm_id', 'bed_supplier_id',
                                     'Bed suppliers',
                                     domain=[('supplier', '=', True)])
    production_orientation = fields.Selection(
        (('milk', 'Milk'), ('meat', 'Meat'), ('mixed', 'Mixed'),
         ('orchard', 'Orchard'), ('other', 'Other')), 'Production orientation')
    cornadizas = fields.Integer('Cornadizas quantity')
    electric_power = fields.Integer('Electric power')
    average_annual_consumption = fields.Integer('Average annual consumption')
    pickup_frequency = fields.Integer('Pickup frequency')
    milk_tank_liter = fields.Integer('Milk tank liter')
    supplies_technician = fields.Many2one('res.users', 'Supplies technician')
    lactating_cows = fields.Many2one('res.partner', 'Lactating cows', domain=[('supplier', '=', True)])
    dry_cows = fields.Many2one('res.partner', 'Dry cows', domain=[('supplier', '=', True)])
    heifers = fields.Many2one('res.partner', 'Heifers', domain=[('supplier', '=', True)])
    bait = fields.Many2one('res.partner', 'Bait', domain=[('supplier', '=', True)])
    feeding_supplier = fields.Many2one('res.partner', 'Feeding supplier',
                                       domain=[('supplier', '=', True)])
    milk_quality_supplier = fields.Many2one('res.partner',
                                            'Milk quality supplier',
                                            domain=[('supplier', '=', True)])
    counselling_supplier = fields.Many2one('res.partner',
                                           'Counselling supplier',
                                           domain=[('supplier', '=', True)])
    clinic_supplier = fields.Many2one('res.partner', 'Clinic supplier',
                                      domain=[('supplier', '=', True)])
    mixer_truck_supplier = fields.Many2one('res.partner',
                                           'Mixer truck supplier',
                                           domain=[('supplier', '=', True)])
    replacement_supplier = fields.Many2one('res.partner',
                                           'Replacement supplier',
                                           domain=[('supplier', '=', True)])
    reproduction_supplier = fields.Many2one('res.partner',
                                            'Reproduction supplier',
                                            domain=[('supplier', '=', True)])
    adsg_certification_supplier = fields.Many2one(
        'res.partner', 'ADSG certification supplier',
        domain=[('supplier', '=', True)])
    special_mix = fields.Integer('Special mix')
    dry_mix = fields.Integer('Dry mix')
    mh = fields.Integer('mh')
    standard_fodder = fields.Integer('Standard fodder')
    concentrate_capacity = fields.Integer('concentrate capacity')
    forage_silos = fields.Integer('Forage silos')
    manure_pit = fields.Integer('Manure pit')
    manure_pit_outdoor = fields.Integer('Manure pit outdoor')
    trailer_access = fields.Boolean('Trailer access')
    employees_quantity = fields.Float('Employees quantity')
    employees_date = fields.Date('Date')
    employee_count_ids = fields.One2many('employee.farm.count', 'partner_id',
                                         'Employees')
    cow_count_ids = fields.One2many('cow.count', 'partner_id', 'Cows')
    heifer_0_3 = fields.Integer('Heifer 0-3 months')
    heifer_3_12 = fields.Integer('Heifer 3-12 months')
    heifer_plus_12 = fields.Integer('Heifer >12 months')
    milk_cow = fields.Integer('Milk cows')
    dry_cow = fields.Integer('Dry cows')
    date_cow = fields.Date('Date')
    milk_analysis_type = fields.Selection(
        (('ligal', 'LIGAL'), ('lila', 'LILA')),
        'Milk analysis type')
    plantation_ids = fields.One2many('res.partner.fields', 'partner_id',
                                     string='Plantations')
    total_net_surface = fields.Float(string="Total Net Surface",
                                     readonly=True, multi=True,
                                     compute="_compute_net_surfaces")
    public_attachment_ids = fields.Many2many(
        'res.partner.attachment',
        'res_partner_attachment_rel',
        'partner_id',
        'attachment_id', domain=[('private', '=', False)])
    private_attachment_ids = fields.Many2many(
        'res.partner.attachment',
        'res_partner_attachment_rel',
        'partner_id',
        'attachment_id', domain=[('private', '=', True)])
    company_ids = fields.One2many("res.company", "partner_id",
                                  "Related Company", readonly=True)
    farm_lots = fields.One2many('lot.partner', 'farm_id')
    product_surfaces = fields.One2many('product.surface.by.partner',
                                       'partner_id', readonly=True,
                                       domain=[('year', '=',
                                                time.strftime('%Y'))])

    @api.one
    def _compute_net_surfaces(self):
        use_obj = self.env['res.partner.fields']
        if self._context.get('use_year', False):
            cur_year = self._context.get('use_year', False) and \
                self._context['use_year'] or str(date.today().year)
        else:
            cur_year = date.today().year
        use_ids = use_obj.search([('partner_id', '=', self.id),
                                  ('year', '=', cur_year)])
        sumtotal = 0.0
        for use_id in use_ids:
            sumtotal += use_id.net_surface
        self.total_net_surface = sumtotal

    @api.model
    def create(self, vals):
        if self._context.get('company_partner', False):
            vals['farm'] = True
        elif vals.get('farm', False):
            # El partner ha sido creado a mano.
            raise exceptions.Warning(
                _('Farm creation error'),
                _('To create farm must do it from the menu farm High'))
        res = super(ResPartner, self).create(vals)
        if vals.get('exploitation_technician', False):
            res.message_subscribe([res.exploitation_technician.partner_id.id])
        if vals.get('secondary_technician', False):
            res.message_subscribe([res.secondary_technician.partner_id.id])
        if res.employees_quantity or res.employees_date:
            count_args = {
                'partner_id': res.id,
                'date': res.employees_date or date.today(),
                'user_id': self.env.user.id,
                'quantity': res.employees_quantity,
                'state': 'current'
            }
            self.env['employee.farm.count'].create(count_args)
        return res

    @api.multi
    def write(self, vals):
        for partner in self:
            if vals.get('employees_quantity', False) or \
                    vals.get('employees_date'):
                current = self.employee_count_ids.filtered(
                    lambda record: record.state == 'current')
                if not current:
                    count_args = {
                        'partner_id': self.id,
                        'date': vals.get('employees_date', date.today()),
                        'user_id': self.env.user.id,
                        'quantity': vals.get('employees_quantity'),
                        'state': 'current'
                    }
                    self.env['employee.farm.count'].create(count_args)
                else:
                    current.sudo().with_context(from_partner=True).\
                        write({'quantity': vals.get('employees_quantity'),
                               'user_id': self.env.user.id})
            if vals.get('heifer_0_3', False) or \
                    vals.get('heifer_3_12', False) or \
                    vals.get('heifer_plus_12', False) or \
                    vals.get('milk_cow', False) or \
                    vals.get('dry_cow', False) or vals.get('date_cow', False):

                count_args = {
                    'partner_id': self.id,
                    'date': vals.get('date_cow', date.today()),
                    'user_id': self.env.user.id,
                    'heifer_0_3': vals.get('heifer_0_3', partner.heifer_0_3),
                    'heifer_3_12': vals.get('heifer_3_12', partner.heifer_3_12),
                    'heifer_plus_12': vals.get('heifer_plus_12', partner.heifer_plus_12),
                    'milk_cow': vals.get('milk_cow', partner.milk_cow),
                    'dry_cow': vals.get('dry_cow', partner.dry_cow),
                    'state': 'current'
                }
                self.env['cow.count'].create(count_args)
                partner.cow_count_ids.write({'state': 'history'})
                last = partner.cow_count_ids.sorted(key=lambda r: r.date)[-1]
                last.state = 'current'
                vals['date_cow'] = last.date
                vals['heifer_0_3'] = last.heifer_0_3
                vals['heifer_3_12'] = last.heifer_3_12
                vals['heifer_plus_12'] = last.heifer_plus_12
                vals['milk_cow'] = last.milk_cow
                vals['dry_cow'] = last.dry_cow

            if vals.get('exploitation_technician', False):
                technician = self.env['res.users'].browse(
                    vals['exploitation_technician'])
                partner.message_subscribe([technician.partner_id.id])
            if vals.get('secondary_technician', False):
                technician = self.env['res.users'].browse(
                    vals['secondary_technician'])
                partner.message_subscribe([technician.partner_id.id])
        return super(ResPartner, self).write(vals)

    @api.multi
    def action_account_assets(self):
        return {
            'domain': "[('company_id','=', " + str(self.company_id.id) + ")]",
            'name': _('Assets'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'tree_view_ref':
                        'account_asset.view_account_asset_asset_tree'},
            'res_model': 'account.asset.asset',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_locations(self):
        return {
            'domain': "[('company_id','='," + str(self.company_id.id) + "), ('usage', '=', 'internal')]",
            'name': _('Locations'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'tree_view_ref':
                        'stock.view_location_tree2',
                        'default_company_id': self.company_id.id},
            'res_model': 'stock.location',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_fields(self):
        return {
            'domain': "[('partner_id','='," + str(self.id) + ")]",
            'name': _('Fincas'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'default_partner_id': self.id},
            'res_model': 'res.partner.fields',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_analytic_plan(self):

        return {
            'domain': "[('company_id','='," + str(self.company_id.id) + ")]",
            'name': _('Analytic Plan'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'default_company_id': self.company_id.id},
            'res_model': 'account.analytic.default',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_private_attachments(self):
        return {
            'domain': "[('id','in'," + str(self.private_attachment_ids.ids) + ")]",
            'name': _('Attachments'),
            'context': {'default_private': True, 'default_recipient_ids': [(6, 0,[self.id])]},
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'res.partner.attachment',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_public_attachments(self):
        return {
            'domain': "[('id','in'," + str(self.public_attachment_ids.ids) + ")]",
            'name': _('Attachments'),
            'context': {'default_recipient_ids': [(6, 0,[self.id])]},
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'res.partner.attachment',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_users_related(self):
        return {
            'domain': "[('company_ids','in'," + str(self.company_ids.ids) + ")]",
            'name': _('Users'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_milk_analysis_report(self):
        return {
            'domain': "[('exploitation_id','='," + str(self.id) + ")]",
            'name': _('Milk analysis'),
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'milk.analysis.report',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_milk_analysis_month_report(self):
        return {
            'domain': "[('exploitation_id','='," + str(self.id) + ")]",
            'name': _('Milk analysis'),
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'milk.analysis.month.report',
            'type': 'ir.actions.act_window',
        }

class ResPartnerCategory(models.Model):

    _inherit = 'res.partner.category'

    description = fields.Text('Description')
    partner_id = fields.Many2many('res.partner',
                                  'res_partner_res_partner_category_rel',
                                  'category_id', 'partner_id', 'Partners')

class ResPartnerFieldsProduct(models.Model):

    _name = 'res.partner.fields.product'

    code = fields.Char()
    name = fields.Char()


class ResPartnerFields(models.Model):
    _name = 'res.partner.fields'
    _rec_name = 'location_name'
    _order = "year desc"

    partner_id = fields.Many2one("res.partner", "Exploitation", required=True)
    province_id = fields.Many2one("res.country.state", "Province Code")
    townhall_id = fields.Char("Town Hall Code")
    added = fields.Boolean("Added")
    zone = fields.Integer("Zone")
    industrial_estate = fields.Char("Industrial Estate")
    plot = fields.Char("Plot")
    enclosure = fields.Char("Enclosure")
    use = fields.Selection(
        [('AG', 'Corrientes y superficies de agua'),
         ('CA', 'Viales'),
         ('CF', u'Cítricos-Frutal'),
         ('CI', u'Cítricos'),
         ('CS', u'Cítricos-Frutal de cáscara'),
         ('CV', u'Cítricos-Viñedo'),
         ('ED', 'Edificaciones'),
         ('FL', u'Frutal de cáscara-Olivar'),
         ('FO', 'Forestal'),
         ('FS', u'Frutal de cáscara'),
         ('FV', 'Frutal de cáscara-Viñedo'),
         ('FY', 'Frutal'),
         ('IM', 'Improductivo'),
         ('IV', u'Invernaderos y cultivos bajo plástico'),
         ('OC', u'Olivar-Cítricos'),
         ('OF', 'Olivar-Frutal'),
         ('OV', 'Olivar'),
         ('PA', 'Pasto arbolado'),
         ('PR', 'Pasto arbustivo'),
         ('PS', 'Pastizal'),
         ('FF', u'Frutal de cáscara-Frutal'),
         ('TA', 'Tierra arable'),
         ('TH', 'Huerta'),
         ('VF', u'Frutal-Viñedo'),
         ('VI', u'Viñedo'),
         ('VO', u'Olivar-Viñedo'),
         ('ZC', 'Zona concentrada'),
         ('ZU', 'Zona urbana'),
         ('ZV', 'Zona censurada')], 'Use', required=True)
    sixpac_surface = fields.Float("Sixpac Surface")
    cap = fields.Float("CAP")
    declared_surface = fields.Float("Declared Surface")
    net_surface = fields.Float("Net Surface")
    product_1 = fields.Many2one('res.partner.fields.product')
    product_2 = fields.Many2one('res.partner.fields.product')
    variety = fields.Integer("Variety")
    location_name = fields.Char("Location Name")
    rent = fields.Float("Rent")
    year = fields.Char("Year")
    custom_id = fields.Char()
    cooperative = fields.Many2one('res.company', related='partner_id.company_id.cooperative_company', store=True)

    _sql_constraints = [
        ('cne_unique', 'unique(custom_id,cooperative)', 'The id is alredery assigned!')
    ]


    @api.multi
    def name_get(self):
        if self._context.get('show_year', False):
            res = [(x.id, u'{}, {} ({})'.format(x.location_name or _('No name'), x.custom_id or '', x.year)) for x in self]
        else:
            res = [(x.id, x.location_name or _('No name')) for x in self]
        return res


class ResPartnerPasswd(models.Model):

    _inherit = 'res.partner.passwd'

    token = fields.Char('Token')
    expire_time = fields.Datetime('Expire time')
    last_sync_date = fields.Date()

class ResPartnerService(models.Model):

    _inherit = 'res.partner.service'

    company_id = fields.\
        Many2one("res.company", "Company",
                 default=
                 lambda self: self.env.user.company_id.cooperative_company)


class ResPartnerAttachment(models.Model):

    _name = 'res.partner.attachment'
    _rec_name = "description"
    _order = "upload_date desc"

    upload_date = fields.\
        Date(default=lambda self: datetime.now().strftime('%Y-%m-%d'),
             required=True)
    author = fields.Many2one('res.users',
                             default=lambda self: self.env.user.id,
                             required=True, readonly=True)
    cooperative = fields.\
        Many2one('res.company',
                 default=
                 lambda self: self.env.user.company_id.cooperative_company,
                 required=True, domain=[('is_cooperative', '=', True)])
    description = fields.Char("Description", size=100)
    recipient_ids = fields.Many2many('res.partner',
                                     'res_partner_attachment_rel',
                                     'attachment_id',
                                     'partner_id', 'recipients',
                                     domain=[('farm', '=', True)])
    private = fields.Boolean()

    @api.multi
    def load_companies(self):
        for attach in self:
            companies = [self.env.user.company_id.partner_id.id]
            companies.\
                extend([x.partner_id.id for x in self.env.user.company_id.child_ids])
            attach.recipient_ids = [(6, 0, companies)]
