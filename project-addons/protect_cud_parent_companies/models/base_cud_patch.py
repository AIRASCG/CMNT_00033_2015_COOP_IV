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


@api.model
def check_company(self):
    if 'company_id' in self._columns.keys():
        if self.env.user.company_id.child_ids:
            allowed_modules = self.env['ir.config_parameter'].search(
                [('key', '=', 'allowed_modules')])
            if not allowed_modules:
                return
            if str(self._model) not in allowed_modules.value.split(','):
                raise exceptions.Warning(
                    _('Error'),
                    _('you can not do the operation on the model %s '
                      'with a parent company') % str(self._model))

models.BaseModel.check_company = check_company

if 'old_create' not in dir(models.BaseModel):
    models.BaseModel.old_create = models.BaseModel.create


@api.model
@api.returns('self', lambda value: value.id)
def create(self, vals):
    self.check_company()
    return self.old_create(vals)

#override create method
models.BaseModel.create = create

if 'old_write' not in dir(models.BaseModel):
    models.BaseModel.old_write = models.BaseModel.write


@api.multi
def write(self, vals):
    self.check_company()
    return self.old_write(vals)

#override write method
models.BaseModel.write = write


if 'old_unlink' not in dir(models.BaseModel):
    models.BaseModel.old_unlink = models.BaseModel.unlink


@api.multi
def unlink(self):
    self.check_company()
    return self.old_unlink()

#override unlink method
models.BaseModel.unlink = unlink
