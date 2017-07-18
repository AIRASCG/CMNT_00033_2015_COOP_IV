# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def migrate(cr, version):
    cr.execute("""INSERT INTO analytic_plan_product_rel (plan_id, product_id)
                  SELECT analytics_id, product_id
                  FROM account_analytic_default
                  WHERE analytics_id IS NOT NULL;""")
