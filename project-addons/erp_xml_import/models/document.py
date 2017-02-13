# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _, exceptions
from openerp.modules.registry import RegistryManager
from lxml import etree
import os
import errno
import logging
import codecs
from StringIO import StringIO
from datetime import datetime
_logger = logging.getLogger(__name__)

TIPO_MAP = {
    'venta': 'out_invoice',
    'compra': 'in_invoice',
    'abono_venta': 'out_refund',
    'abono_compra': 'in_refund'
}


class ErpXmlDocument(models.Model):

    _name = 'erp.document'

    name = fields.Char()
    state = fields.Selection(
        (('new', 'New'), ('imported', 'Imported'), ('error', 'Error')),
        default='new')
    type = fields.Selection(
        (('partner', 'Partner'),
         ('invoice', 'Invoice'),
         ('undefined', 'Undefined')))
    errors = fields.Text()
    document = fields.Text()

    @api.multi
    def parse_partner(self, partner):
        coop_partner = self.env['res.partner'].search(
            [('erp_reference', '=', partner['codigo_coop'])])
        if not coop_partner:
            raise Exception(
                _('Code error'),
                _('Cooperative with code %s not found') %
                partner['codigo_coop'])
        country = self.env['res.country'].search(
            [('code', '=', partner['cod_pais'])])
        partner_data = {
            'name': partner['nombre'],
            'customer': partner['cliente'],
            'supplier': partner['proveedor'],
            'farm': partner['explotacion'],
            'active': partner['activo'],
            'erp_reference': partner['codigo'],
            'country_id': country.id,
        }
        if 'nif' in partner.keys():
            partner_data['vat'] = partner['cod_pais'] + partner['nif']
        if 'calle' in partner.keys():
            partner_data['street'] = partner['calle']
        if 'cp' in partner.keys():
            partner_data['zip'] = partner['cp']
        if 'tlfn' in partner.keys():
            partner_data['phone'] = partner['tlfn']
        if 'poblacion' in partner.keys():
            partner_data['city'] = partner['poblacion']
        if 'cod_provincia' in partner.keys() and partner['cod_provincia']:
            state = self.env['res.country.state'].search(
                [('code', '=', partner['cod_provincia'])])
            if not state:
                raise Exception(
                    _('Code error'),
                    _('State with code %s not found') %
                    partner['cod_provincia'])
            partner_data['state_id'] = state.id
        if 'email' in partner.keys():
            partner_data['email'] = partner['email']
        if 'fax' in partner.keys():
            partner_data['fax'] = partner['fax']
        if 'notas' in partner.keys():
            partner_data['comment'] = partner['notas']
        if 'web' in partner.keys():
            partner_data['website'] = partner['web']
        if 'socio_relacionado' in partner.keys():
            partner_data['partner_of'] = partner['socio_relacionado']
        created_partner = self.env['res.partner'].search(
            [('erp_reference', '=', partner['codigo'])])
        if created_partner:
            created_partner.write(partner_data)
        else:
            if partner.get('explotacion', False):
                # se crea la compañía y se asigna a created_partner el partner
                new_company = self.env['res.company'].create(
                    {'name': partner['nombre'],
                     'parent_id': coop_partner.company_id.id})
                created_partner = new_company.partner_id
                created_partner.write(partner_data)
            elif partner.get('cliente', False) or partner.get('proveedor', False):
                partner_data['company_id'] = coop_partner.company_id.id
                self.env['res.partner'].create(partner_data)

    @api.multi
    def parse_invoice(self, invoice):
        invoice_data = {}
        invoice_data['invoice_number'] = invoice['numero']
        invoice_data['number'] = invoice['numero']
        invoice_data['currency_id'] = self.env.user.company_id.currency_id
        company_partner = self.env['res.partner'].search(
            [('erp_reference', '=', invoice['codigo_explo'])])
        if not company_partner:
            raise Exception(
                _('partner not found'),
                _('Partner with code %s not found') % invoice['codigo_explo'])
        created_invoice = self.env['account.invoice'].search(
            [('number', '=', invoice_data['number']),
             ('company_id', '=', company_partner.company_id.id)])
        if created_invoice:
            if 'eliminar' in invoice and invoice['eliminar']:
                created_invoice.unlink()
                return
        invoice_data['company_id'] = company_partner.company_id.id
        partner = self.env['res.partner'].search(
            [('erp_reference', '=', invoice['codigo_empresa'])])
        if not partner:
            raise Exception(
                _('partner not found'),
                _('Partner with code %s not found') %
                invoice['codigo_empresa'])
        invoice_data['partner_id'] = partner.id
        invoice_data['date_invoice'] = datetime.strptime(
            invoice['fecha_factura'], '%Y-%m-%d')

        if 'notas' in invoice:
            invoice_data['comment'] = invoice['notas']
        invoice_data['type'] = TIPO_MAP[invoice['tipo']]
        invoice_data['invoice_line'] = []
        for line in invoice['lines']:
            line_data = {}
            if 'referencia_interna' in line:
                product = self.env['product.product'].with_context(
                    force_company=invoice_data['company_id']).search(
                    [('default_code', '=', line['referencia_interna'])])
                if not product:
                    raise Exception(
                        _('Reference error'),
                        _('Product with code %s not found') %
                        line['referencia_interna'])
                line_data['product_id'] = product.id
                if invoice_data['type'] in ('out_invoice', 'out_refund'):
                    account = product.property_account_income or \
                        product.categ_id.property_account_income_categ
                else:
                    account = product.property_account_expense or \
                        product.categ_id.property_account_expense_categ
            else:
                property_obj = self.env['ir.property'].with_context(
                    force_company=invoice_data['company_id'])
                if invoice_data['type'] in ('out_invoice', 'out_refund'):
                    account = property_obj.get('property_account_income_categ',
                                               'product.category')
                else:
                    account = property_obj.get(
                        'property_account_expense_categ', 'product.category')
            line_data['account_id'] = account.id
            line_data['name'] = line['concepto']
            line_data['quantity'] = float(line['cantidad'])
            line_data['price_unit'] = float(line['precio_unidad'])
            line_data['discount'] = float(line['descuento'])
            taxes = []
            for tax in line['taxes']:
                invoice_type_to_tax_type = {
                    'venta': 'S',
                    'compra': 'P',
                    'abono_venta': 'S',
                    'abono_compra': 'P'
                }
                if tax['tipo'] == 'venta':
                    tax_code = 'S_IVA%sB' % \
                        str(int(float(tax['tipo_aplicado'])))
                elif tax['tipo'] == 'compra':
                    tax_code = 'P_IVA%s_BC' % \
                        str(int(float(tax['tipo_aplicado'])))
                elif tax['tipo'] == 'recargo_eq':
                    tax_type = invoice_type_to_tax_type[invoice['tipo']]
                    tax_code = '%s_REQ%s' % (tax_type, tax['tipo_aplicado'])
                elif tax['tipo'] == 'irpf':
                    tax_type = invoice_type_to_tax_type[invoice['tipo']]
                    tax_code = '%s_IRPF%s' % \
                        (tax_type, str(int(float(tax['tipo_aplicado']))))
                tax_r = self.env['account.tax'].search(
                    [('description', 'ilike', tax_code),
                     ('company_id', '=', invoice_data['company_id'])])
                if not tax_r:
                    raise Exception(
                        _('Reference error'),
                        _('tax with type %s and amount %s not found for the company %s') %
                        (tax['tipo'], tax['tipo_aplicado'], invoice_data['company_id']))
                taxes.append(tax_r.id)
            if taxes:
                line_data['invoice_line_tax_id'] = [(6, 0, taxes)]
            invoice_data['invoice_line'].append((0, 0, line_data))
        onch_dict = self.env['account.invoice'].onchange_partner_id(
            'in_invoice', invoice_data['partner_id'],
            company_id=invoice_data['company_id'])
        if 'value' in onch_dict:
            invoice_data.update({k: onch_dict['value'][k]
                                 for k in onch_dict['value']
                                 if k not in invoice_data})
        onch_dict = self.env['account.invoice'].onchange_company_id(
            invoice_data['company_id'], False, 'in_invoice', False, False)
        if 'value' in onch_dict:
            invoice_data.update({k: onch_dict['value'][k]
                                 for k in onch_dict['value']
                                 if k not in invoice_data})
        if created_invoice:
            created_invoice.invoice_line.unlink()
            created_invoice.write(invoice_data)
        else:
            self.env['account.invoice'].create(invoice_data)

    @api.model
    def import_data(self):

        docs = self.search([('state', 'in', ('new', 'error')),
                            ('type', '!=', 'undefined')])
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    '..', 'data'))
        for doc in docs:
            with_error = False
            with api.Environment.manage():
                with RegistryManager.get(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    #Se hace browse con un env diferente para guardar cambios
                    doc_ = self.with_env(new_env).browse(doc.id)
                    if not doc.document:
                        continue
                    schema_file = doc.type == 'partner' and 'xsd/partner.xsd' or \
                        'xsd/invoice.xsd'
                    schema_file = '%s%s%s' % (data_path, os.sep, schema_file)
                    with open(schema_file, 'r') as f:
                        xmlschema_doc = etree.parse(f)
                        xmlschema = etree.XMLSchema(xmlschema_doc)
                        f2 = StringIO(doc.document.encode('utf-8'))
                        xml_doc = etree.parse(f2)
                        try:
                            xmlschema.assertValid(xml_doc)
                        except etree.DocumentInvalid as e:
                            doc.errors += '\n%s' % str(e)
                            doc.state = 'error'
                            with_error = True
                            continue
                        if doc.type == 'partner':
                            for partner_element in xml_doc.getroot().iter('partner'):
                                if with_error:
                                    break
                                partner = {}
                                for el in partner_element.iter():
                                    if el.tag in ('cliente', 'proveedor',
                                                  'explotacion', 'activo'):
                                        partner[el.tag] = bool(int(el.text))
                                    else:
                                        partner[el.tag] = el.text
                                try:
                                    doc_.parse_partner(partner)
                                except Exception as e:
                                    doc.errors += '\n%s' % str(e)
                                    doc.state = 'error'
                                    new_env.cr.rollback()
                                    with_error = True
                                    continue

                        elif doc.type == 'invoice':
                            for invoice_element in \
                                    xml_doc.getroot().iterchildren('invoice'):
                                if with_error:
                                    break
                                invoice = {}
                                for el in invoice_element.iterchildren():
                                    if el.tag in ('eliminar'):
                                        invoice[el.tag] = bool(int(el.text))
                                    elif el.tag == 'lines':
                                        invoice[el.tag] = []
                                        for il in el.iterchildren(tag='line'):
                                            line = {}
                                            for il_el in il.iterchildren():
                                                if il_el.tag == 'taxes':
                                                    line['taxes'] = []
                                                    for tax_l in il_el.iterchildren(
                                                            tag='tax'):
                                                        tax = {}
                                                        for tax_l in \
                                                                tax_l.iterchildren():
                                                            tax[tax_l.tag] = tax_l.text
                                                        line['taxes'].append(tax)

                                                else:
                                                    line[il_el.tag] = il_el.text
                                            invoice[el.tag].append(line)
                                    else:
                                        invoice[el.tag] = el.text

                                try:
                                    doc_.parse_invoice(invoice)
                                except Exception as e:
                                    doc.errors += '\n%s' % str(e)
                                    doc.state = 'error'
                                    new_env.cr.rollback()
                                    with_error = True
                                    continue
                    if not with_error:
                        doc.state = 'imported'
                        new_env.cr.commit()

    @api.multi
    def move_imported_files(self, importation_folder, process_folder):
        now = datetime.now()
        final_folder = process_folder + os.sep + str(now.year) + os.sep + \
            str(now.month)
        for doc in self:
            if doc.state == 'imported':
                try:
                    os.makedirs(final_folder)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and \
                            os.path.isdir(final_folder):
                        pass
                from_file = '%s%s%s' % (importation_folder, os.sep, doc.name)
                to_file = '%s%s%s' % (final_folder, os.sep, doc.name)
                os.rename(from_file, to_file)

    @api.model
    def import_files(self):
        folders = [x.xml_route for x in self.env['res.company'].search(
            [('xml_route', '!=', False)])]
        for folder in folders:
            if not folder:
                _logger.error('Not found config parameter erpxml.folder')
                return
            importation_folder = '%s%slecturas' % (folder, os.sep)
            process_folder = '%s%sprocesados' % (folder, os.sep)
            if 'lecturas' not in os.listdir(folder):
                os.mkdir(importation_folder)
            if 'procesados' not in os.listdir(folder):
                os.mkdir(process_folder)
            import_files = [x for x in os.listdir(importation_folder)
                            if x.endswith('.xml')]
            docs = self.env['erp.document']
            for import_file in import_files:
                errors = []
                doc = self.env['erp.document'].search(
                    [('name', '=', import_file),
                     ('state', 'in', ('new', 'error'))])
                if not doc:
                    doc_vals = {
                        'name': import_file,
                        'state': 'new',
                    }
                    doc = self.env['erp.document'].create(doc_vals)
                docs += doc
                with codecs.open(
                        '%s%s%s' % (importation_folder, os.sep, import_file),
                        'r', 'iso-8859-1') as f:
                    doc_content = f.read()
                    if 'partner.xsd' in doc_content:
                        type = 'partner'
                    elif 'invoice.xsd' in doc_content:
                        type = 'invoice'
                    else:
                        errors.append(
                            _('Type not found: xsd not found in xml file'))
                        type = 'undefined'
                    state = 'new'
                    if errors:
                        state = 'error'
                    doc.write({'type': type, 'document': doc_content,
                               'errors': '\n'.join(errors), 'state': state})
            self.import_data()
            docs.move_imported_files(importation_folder, process_folder)
