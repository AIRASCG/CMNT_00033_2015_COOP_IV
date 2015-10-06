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
from openerp import models, fields, api, exceptions, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    is_seed_supplier = fields.Boolean('Seed supplier')
    is_bed_supplier = fields.Boolean('Bed supplier')
    is_various_supplier = fields.Boolean('Various supplier')
    is_external_service_supplier = fields.Boolean('External service supplier')
    is_insurance_service_supplier = fields.Boolean(
        'Insurance service supplier')
    is_clean_supplier = fields.Boolean('Clean supplier')
    is_raw_material_supplier = fields.Boolean('Raw material supplier')
    is_vet_supplier = fields.Boolean('Vet supplier')
    is_chiropody_supplier = fields.Boolean('Chiropody supplier')
    is_financial_service_supplier = fields.Boolean(
        'Financial service supplier')
    is_energy_supplier = fields.Boolean('Energy supplier')
    is_machine_supplier = fields.Boolean('Machine supplier')
    is_maintenance_supplier = fields.Boolean('Maintenance supplier')
    is_lab_supplier = fields.Boolean('Lab supplier')
