# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""
        UPDATE lot_content
        SET theorical_kg_ration=_theorical_kg_ration,
            theorical_ms=_theorical_ms,
            theorical_enl=_theorical_enl,
            theorical_pb=_theorical_pb""")
