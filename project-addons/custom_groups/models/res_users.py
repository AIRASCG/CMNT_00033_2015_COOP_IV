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
from openerp import models, fields, api, exceptions, _, SUPERUSER_ID
from lxml import etree


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.one
    @api.depends('groups_id')
    def _get_user_profile(self):
        admin_id = self.env.ref('custom_groups.group_admin')
        self.profile = False
        if admin_id in self.groups_id:
            self.profile = 'admin'
        else:
            adtech_id = self.env.ref('custom_groups.group_tech_mngnt')
            if adtech_id in self.groups_id:
                self.profile = 'tech_admin'
            else:
                feedTec_id = self.env.ref('custom_groups.group_tech_feed')
                if feedTec_id in self.groups_id:
                    self.profile = 'tech_feed'
                else:
                    salesTec = self.env.ref('custom_groups.group_tech_sales')
                    if salesTec in self.groups_id:
                        self.profile = 'tech_sales'
                    else:
                        farmer_id = self.env.ref('custom_groups.group_rancher')
                        if farmer_id in self.groups_id:
                            self.profile = 'farmer'

    profile = fields.Selection([('admin', 'Administrator'),
                                ('tech_admin', 'Technical management'),
                                ('tech_feed', 'Technical feed'),
                                ('tech_sales', 'Technical sales'),
                                ('farmer', 'Farmer')], readonly=True,
                                compute="_get_user_profile", store=True)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(ResUsers, self).fields_view_get(view_id=view_id,
                                                    view_type=view_type,
                                                    toolbar=toolbar,
                                                    submenu=submenu)
        view_obj = self.env.ref('base.view_users_form')
        if view_type == 'form' and self.env.user.id != SUPERUSER_ID and view_id == view_obj.id:
            view = etree.XML(res['arch'])
            for separator in view.xpath("//notebook/page[1]/group[2]/separator[@string!='" + _("User types") + "']"):
                separator.set("modifiers", '{"invisible": true}')
            id_1 = self.env.ref('custom_groups.group_admin').id
            id_2 = self.env.ref('custom_groups.group_tech_mngnt').id
            id_3 = self.env.ref('custom_groups.group_tech_feed').id
            id_4 = self.env.ref('custom_groups.group_tech_sales').id
            id_5 = self.env.ref('custom_groups.group_rancher').id
            custom_names = ['in_group_%s' % x for x in (id_1, id_2, id_3,
                                                        id_4, id_5)]
            for field in view.xpath("//field[starts-with(@name,'in_group')]"):
                if field.get('name') not in (custom_names):
                    field.set("modifiers", '{"invisible": true}')

            for field in view.xpath("//field[starts-with(@name,'sel_groups')]"):
                field.set("modifiers", '{"invisible": true}')
            res['arch'] = etree.tostring(view)
        if view_type == 'form' and view_id == view_obj.id:
            view = etree.XML(res['arch'])
            description_text = \
                _("<p>Desde aquí se permite la gestión (creación, borrado y "
                  "modificaciones) de usuarios con sus contraseñas, y la "
                  "asignación de esos usuarios a grupos de usuarios, cada uno "
                  "de los cuales tiene un conjunto de permisos distinto.</p>"
                  "<p><b>Administrador:</b> Acceso a todo tipo de "
                  "funcionalidades de la administración, puede asociar "
                  "nuevos permisos a otros usuarios, generar informes y "
                  "visualizar todo tipo de datos.</p>"
                  "<p><b>Técnico gestión:</b> Acceso a todas las "
                  "funcionalidades de la administración, excepto a la "
                  "gestión y control de usuarios.</p>"
                  "<p><b>Técnico de alimentación:</b> Acceso a las "
                  "funcionalidades del módulo de alimentación y visitas.</p>"
                  "<p><b>Técnico comercial:</b> Acceso a las funcionalidades "
                  "del módulo de visitas y a la ficha de las explotaciones."
                  "</p>"
                  "<p><b>Ganadero:</b> Este perfil únicamente accede a "
                  "determinados datos de su explotación.</p>")
            separator = view.xpath("//notebook/page[1]/group[2]/separator[@string='" + _("User types") + "']")[0]
            separator.addnext(etree.XML('<group colspan="4"><div>%s</div></group>' % description_text))
            res['arch'] = etree.tostring(view)
        return res
