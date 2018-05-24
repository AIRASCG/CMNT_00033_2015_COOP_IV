# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re


def migrate(cr, version):
    cr.execute(
        """ALTER TABLE phytosanitary rename column registry_number to registry_number_old;""")
