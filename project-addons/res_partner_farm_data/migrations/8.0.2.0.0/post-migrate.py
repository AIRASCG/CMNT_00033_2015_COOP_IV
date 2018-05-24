# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO res_partner_fields_product(code, name)
        SELECT distinct product_code, product_name
        FROM res_partner_fields
        WHERE product_code IS NOT NULL
        """)

    cr.execute(
        """
        UPDATE res_partner_fields
        SET product_1 = fields_product.id
        FROM (select id, code from res_partner_fields_product) AS fields_product
        WHERE res_partner_fields.product_code = fields_product.code
        """)
