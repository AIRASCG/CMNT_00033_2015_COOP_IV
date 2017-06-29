# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
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
from openerp import models, api, exceptions, _


class LotReport(models.AbstractModel):
    _name = 'report.res_partner_farm_data.lot_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'res_partner_farm_data.lot_report')
        objs = self.env[report.model].browse(self._ids)
        lots = {}

        for o in objs:
            z = zip()
            lots[o.id] = z
            all_products = []
            if not o.lot_details:
                raise exceptions.Warning(_("Cannot print report without lots"))
            # Cabeceras
            headers = ['Ingrediente']
            for detail in o.lot_details:
                headers.append(detail.name)
                for content in detail.lot_contents:
                    if content.product_id not in all_products:
                        all_products.append(content.product_id)

            headers.extend(['Total', u'Ración media'])
            z.append(headers)

            # Productos
            for product in all_products:
                body = [product]
                subtotal = 0.0
                for detail in o.lot_details:
                    content_detail = self.env['lot.content'].search([('product_id', '=', product.id), ('detail_id', '=', detail.id)])
                    amount = content_detail and content_detail[0].kg_ration * detail.rations_make_number or 0
                    body.append(amount)
                    subtotal += amount
                body.append(subtotal)
                if o.number_milking_cows:
                    body.append(round(subtotal / o.number_milking_cows, 2))
                else:
                    body.append(0)
                z.append(body)

            #Pie
            footer = [""]
            for index in range(1, len(z[0])):
                total_col = 0
                for line in z[1:]:
                    total_col += line[index]
                footer.append(total_col)
            z.append(footer)

            tab_struct = [
                ('a', 'Nº raciones hechas: ', 'lot.rations_make_number', 'sum([x.rations_make_number for x in lot_details])'),
                ('b', 'Kg MF en el carro:', 'lot.kf_mf_carriage', 'sum([x.kf_mf_carriage for x in lot_details])'),
                ('c', 'Sobrantes (kg)', 'lot.surplus', 'sum([x.surplus for x in lot_details])'),
                ('d', 'Nº vacas a comer:', 'lot.cows_eat_number', 'sum([x.cows_eat_number for x in lot_details])'),
                ('e', 'Nº vacas en ordeño:', 'lot.number_milking_cows', 'sum([x.number_milking_cows for x in lot_details])'),
                ('f', 'Nº vacas al tanque:', 'lot.cows_tank_number', 'sum([x.cows_tank_number for x in lot_details])'),
                ('g', 'Ingesta kg MF/vaca y día:', 'lot.imf_real', '(table["b"]["total"] - table["c"]["total"]) / (table["e"]["total"] + (table["d"]["total"] - table["e"]["total"]) / 2)'),
                ('h', 'Ingesta kg MS/vaca y día:', 'lot.perc_ms_ration_anal==0 and lot.ims_total_kg_cow_day_real or lot.ims_total_kg_cow_day_anal', 'sum([table["h"][x] * table["d"][x] for x in table["h"].keys() if x not in ("title", "total")]) / table["d"]["total"]'),
                ('i', 'IMS de punteo (kg/vaca y día):', 'lot.ims_plucking_kg_cow_day_real', 'sum([table["i"][x] * table["d"][x] for x in table["i"].keys() if x not in ("title", "total")]) / table["d"]["total"]'),
                ('j', 'IMS Total (Kg/vaca y día):', 'lot.perc_ms_ration_anal==0 and lot.ims_unifed_kg_cow_day_real or lot.ims_unifed_kg_cow_day_anal', 'sum([table["j"][x] * table["d"][x] for x in table["j"].keys() if x not in ("title", "total")]) / table["d"]["total"]'),
                ('s', 'Litros al tanque:', 'lot.tank_liters', 'sum([x.tank_liters for x in lot_details]) > 0 and sum([x.tank_liters for x in lot_details]) or lot.lot_id.liters_produced_per_day'),
                ('t', 'Litros retirados:', 'lot.retired_liters', 'sum([x.retired_liters for x in lot_details])'),
                ('u', 'Litros autoconsumo:', 'lot.liters_on_farm_consumption', 'sum([x.liters_on_farm_consumption for x in lot_details])'),
                ('k', 'Producción por vaca lactante:', 'lot.milk_cow_production', '(table["s"]["total"] + table["t"]["total"] + table["u"]["total"]) / table["e"]["total"]'),
                ('l', 'Producción corregida por vaca lactante:', 'lot.milk_cow_production_corrected', '(12.82 * table["k"]["total"] * (o.mg / 100)) + (7.13 * table["k"]["total"] * (o.mp / 100) + (0.323 * table["k"]["total"]))'),
                ('m', 'Producción por vaca presente:', 'lot.eat_cow_production', '(table["s"]["total"] + table["t"]["total"] + table["u"]["total"]) / (table["d"]["total"] + o.number_dry_cows)'),
                ('n', 'Producción corregida por vaca presente:', 'lot.eat_cow_production_corrected', '(12.82 * table["m"]["total"] * (o.mg / 100)) + (7.13 * table["m"]["total"] * (o.mp / 100) + (0.323 * table["m"]["total"]))'),
                ('o', 'Producción por cubículo:', 'lot.cubicle_production', '(lot.tank_liters + lot.liters_on_farm_consumption + lot.retired_liters) / lot.number_cubicles_in_lot'),
                ('p', 'Producción corregida por cubículo:', 'lot.cubicle_production_corrected', '(12.82 * lot.cubicle_production * (o.mg / 100.0)) + (7.13 * lot.cubicle_production * (o.mp / 100.0) + (0.323 * lot.cubicle_production))'),
                ('q', 'IC (litros/kg MS:', 'lot.perc_ms_ration_anal==0 and lot.ic_liters_kg_real or lot.ic_liters_kg_anal', '((table["s"]["total"] + table["t"]["total"] + table["u"]["total"]) / table["e"]["total"]) / table["j"]["total"]'),
                ('r', 'IC corregido (litros/kg MS:', 'lot.ic_corrected_liters_kg_theo', 'table["l"]["total"] / table["h"]["total"]'),
                ('v', 'Grs grasa/vaca y día', '0', 'table["k"]["total"] * o.mg * 10'),
                ('w', 'Grs proteína/vaca y día', '0', 'table["k"]["total"] * o.mp * 10'),
                ('y', 'Coste ración (€/vaca y día):', 'lot.ration_carriage_cost_eur_cow_day_real', 'sum([x.cows_eat_number * x.ration_carriage_cost_eur_cow_day_real for x in lot_details]) / table["d"]["total"]'),
                ('x', 'Coste ración (€/100 litros):', 'lot.ration_carriage_cost_eur_liter_real', '(table["y"]["total"] / table["k"]["total"]) * 100'),
                ('z', 'Ingreso leche/vaca y día:', 'lot.ingress_milk_cow_day', '(o.liters_sold_per_day * o.milk_price / 1000) / table["e"]["total"]'),
                ('aa', 'Diferencia :', 'lot.diff_ing_cost', 'table["z"]["total"] - table["y"]["total"]'),
                ('ab', '% alimentación sobre ingresos leche:', 'lot.perc_feed_milk_ingress', '(table["y"]["total"] / table["z"]["total"]) * 100.0'),
                ('ac', '% alimentación comprada sobre ingresos leche:', '0', '0'),
                ('ad', '% concentrado sobre ingresos leche:', '0', '0'),
                ('ae', 'Lts producidos/kg de concentrado gastado:', '0', '0'),
                ('af', 'Punto umbral de este lote (destino matadero):', 'lot.lot_threshold_point_slaughterhouse', '(table["y"]["total"] / o.milk_price) * 1000'),
                ('ag', 'Punto umbral de este lote (destino lote secas):', 'lot.lot_threshold_point_dry', '((table["y"]["total"] - o.dry_cow_ration_cost) / o.milk_price) * 1000'),
            ]
            struct_checks = {
                'q': 'table["e"]["total"] != 0.0 and table["j"]["total"] != 0.0',
                'ab': 'table["z"]["total"] != 0.0',
                'af': 'o.milk_price != 0.0',
                'ag': 'o.dry_cow_ration_cost != 0.0 and o.milk_price != 0.0'
            }
            table = {}

            for line_struct in tab_struct:
                checked = True
                table[line_struct[0]] = {'title': line_struct[1]}
                lot_details = o.lot_details
                if struct_checks.get(line_struct[0], False):
                    if not eval(struct_checks[line_struct[0]]):
                        checked = False
                for lot_ind in range(0, len(lot_details)):
                    lot = lot_details[lot_ind]
                    if checked:
                        try:
                            table[line_struct[0]][lot_ind] = round(eval(line_struct[2]), 2)
                        except ZeroDivisionError:
                            table[line_struct[0]][lot_ind] = 0.0
                    else:
                        table[line_struct[0]][lot_ind] = 0.0
                if checked:
                    try:
                        table[line_struct[0]]['total'] = round(eval(line_struct[3]), 2)
                    except ZeroDivisionError:
                        table[line_struct[0]]['total'] = 0.0
                else:
                    table[line_struct[0]]['total'] = 0.0

        table_keys = sorted(table.keys(), key=lambda item: (len(item), item))

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': objs,
            'lots': lots,
            'table': table,
            'table_keys': table_keys,
        }
        return report_obj.render('res_partner_farm_data.lot_report',
                                 docargs)
