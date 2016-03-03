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


class LotAnalysis(models.Model):

    _name = 'lot.analysis'

    def _get_company(self):
        return self.env.user.company_id

    name = fields.Char('Reference', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=_get_company)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    tipo_material = fields.Selection(
        (('hierba', 'Silo hierba'), ('maiz', 'Silo maiz'),
         ('unifeed', 'Mezcla unifeed')), 'Tipo de material')
    cooperative_id = fields.Many2one('res.partner', 'Cooperative')
    lab_id = fields.Many2one('res.partner', 'Laboratory')
    explotation_id = fields.Many2one('res.partner', 'Explotation')
    year = fields.Integer('Year')
    product_name = fields.Char('Product name')
    notes = fields.Text('Notes')
    sampling_date = fields.Date('Sampling date')
    analysis_date = fields.Date('Analysis date')
    cut_number = fields.Integer('cut number')
    dry_material = fields.Float('Dry material')
    cinder = fields.Float('Cinder')
    enl = fields.Float('Enl')
    ufl = fields.Float('UFL')
    pb = fields.Float('PB')
    pbn = fields.Float('PBn')
    ps = fields.Float('PS')
    starch = fields.Float('Starch')
    grain_equivalence = fields.Float('Grain equivalence')
    ee = fields.Float('EE')
    fb = fields.Float('FB')
    fad = fields.Float('FAD')
    fnd = fields.Float('FND')
    lignina = fields.Float('Lignina')
    digestibility = fields.Float('Digestibility')
    vrf = fields.Float('VRF')
    pdie = fields.Float('PDIE')
    pdin = fields.Float('PDIN')
    ph = fields.Float('pH')
    ph_stability = fields.Float('pH stability')
    conservation_index = fields.Float('Conservation index')
    lactic_acid = fields.Float('Lactic acid')
    acetic_acid = fields.Float('Acetic acid')
    butyric_acid = fields.Float('Butyric acid')
    ecoli_absence = fields.Boolean('E coli absence')
    ecoli_unquantifiable = fields.Boolean('E coli unquantifiable')
    ecoli_value = fields.Text('E coli value')
    salmonella_absence = fields.Boolean('Salmonella absence')
    salmonella_unquantifiable = fields.Boolean('Salmonella unquantifiable')
    salmonella_value = fields.Text('Salmonella value')
    staphylococci = fields.Float('Staphylococci')
    mold = fields.Float('Mold')
    clostridium = fields.Float('Clostridium')
    yeast = fields.Float('Yeast')
    enterobacteriaceae = fields.Float('Enterobacteriaceae')
    calcium = fields.Float('Calcium')
    phosphor = fields.Float('Phosphor')
    sodium = fields.Float('Sodium')
    potassium = fields.Float('Potassium')
    magnesium = fields.Float('Magnesium')
    iron = fields.Float('Iron')
    copper = fields.Float('Copper')
    zinc = fields.Float('Zinc')
    manganese = fields.Float('Manganese')
    chlorine = fields.Float('Chlorine')
    sulfur = fields.Float('Sulfur')
    zearelenone = fields.Float('Zearelenone')
    vomitoxin = fields.Float('Vomitoxin')
    afla_b1 = fields.Float('AFLA B1')
