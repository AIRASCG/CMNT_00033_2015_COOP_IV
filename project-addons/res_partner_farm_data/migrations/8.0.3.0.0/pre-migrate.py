# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """ALTER TABLE output_quota DROP CONSTRAINT output_quota_quota_uniq;""")
