# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re


def migrate(cr, version):
    cr.execute(
        """SELECT id, bacteriology, cs, cryoscope, urea
           FROM milk_analysis_line;""")
    for line in cr.fetchall():
        line_id = line[0]
        new_line_vals = []
        for value in line[1:]:
            if value:
                new_value = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', str(value))
                if new_value:
                    new_value = new_value[0]
                else:
                    new_value = '0'  # Algunos campos tienen como valor -
            else:
                new_value = '0'
            new_line_vals.append(new_value)
        print 'Antigua linea %s' % str(line[1:])
        print 'Nueva linea   %s' % str(new_line_vals)
        cr.execute(
            """UPDATE milk_analysis_line
               SET bacteriology = {}, cs= {}, cryoscope = {}, urea = {}
               WHERE id={};""".format(*(new_line_vals + [line_id])))
    cr.execute("""DROP VIEW IF EXISTS milk_analysis_report;""")
    cr.execute("""DROP VIEW IF EXISTS milk_analysis_month_report;""")
    cr.execute("""ALTER TABLE milk_analysis_line
                 ALTER bacteriology TYPE double precision USING bacteriology::double precision,
                 ALTER cs TYPE double precision USING cs::double precision,
                 ALTER cryoscope TYPE double precision USING cryoscope::double precision,
                 ALTER urea TYPE double precision USING urea::double precision;""")
