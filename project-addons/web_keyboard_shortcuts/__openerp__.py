# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Keyboard shortcuts',
    'version': '1.1',
    'category': 'Tools',
    'description': """
    left alt + left shift + c : Create ;
    left alt + left shift + d : Discard ;
    left alt + left shift + e : Edit ;
    left alt + left shift + s : Save ;
    left alt + left shift + arrow up : previous object ;
    left alt + left shift + arrow down : next object ;
    left alt + left shift + enter : one2many form save and create ;

    """,
    "author": "Elico Corp",
    "website": "http://www.openerp.net.cn",
    'depends': ['web'],
    'data': ['assets.xml'],
    'installable': True,
    'active': True,
}
