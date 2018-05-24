# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""INSERT INTO phytosanitary_registry_number(name)
                  SELECT distinct registry_number_old from phytosanitary""")
    cr.execute("""
        UPDATE phytosanitary set registry_number = reg_num.id
        FROM phytosanitary_registry_number reg_num
        WHERE registry_number_old=reg_num.name""")
