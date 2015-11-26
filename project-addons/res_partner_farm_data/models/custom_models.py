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
from datetime import date

class HistoricalModel(models.Model):
    """
        Los modelos que hereden de esta clase deberán tener un campo state con al
        menos un estado history, un campo date y un campo user destinados a registrar los cambios
    """

    _auto = True
    _register = False # not visible in ORM registry, meant to be python-inherited only
    _transient = False # True in a TransientModel

    @api.multi
    def write(self, vals):
        for record in self:
            vals['sequence'] = record.sequence + 1
            vals['date'] = date.today()
            vals['user_id'] = self.env.user.id
            new = record.copy(vals)
        return super(HistoricalModel, self).write({'state': 'history'})
