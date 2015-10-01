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
from openerp import models
from openerp.addons.auth_signup.res_users import res_users, now

def action_reset_password(self, cr, uid, ids, context=None):
    """ create signup token for each user, and send their signup url by email """
    # prepare reset password signup
    res_partner = self.pool.get('res.partner')
    partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context)]
    res_partner.signup_prepare(cr, uid, partner_ids, signup_type="reset", expiration=now(days=+1), context=context)

    if not context:
        context = {}

    # send email to users with their signup url
    template = False
    if context.get('create_user'):
        try:
            # get_object() raises ValueError if record does not exist
            template = self.pool.get('ir.model.data').get_object(cr, uid, 'custom_email_template', 'set_password_email')
        except ValueError:
            pass
    if not bool(template):
        template = self.pool.get('ir.model.data').get_object(cr, uid, 'custom_email_template', 'reset_password_email')
    assert template._name == 'email.template'

    for user in self.browse(cr, uid, ids, context):
        if not user.email:
            raise osv.except_osv(_("Cannot send email: user has no email address."), user.name)
        self.pool.get('email.template').send_mail(cr, uid, template.id, user.id, force_send=True, raise_exception=True, context=context)


class ResUsersMonkeypatch(models.Model):
    _name = 'res.users.monkeypatch'
    _description = 'res users model monkeypatch'


    def _register_hook(self, cr):
        res_users.action_reset_password = action_reset_password
        return super(ResUsersMonkeypatch, self)._register_hook(cr)
