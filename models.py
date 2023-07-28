from openerp import fields, models
import base64
import requests
from collections import OrderedDict
import json

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_json_qr(self):
        for rec in self:
            dict_invoice = OrderedDict()  # Usar OrderedDict en lugar de {}
            if rec.type in ['out_invoice','out_refund'] and rec.afip_auth_code != '':
                try:
                    
                    dict_invoice = OrderedDict([
                        ("ver", 1),
                        ("fecha", str(rec.date_invoice)),
                        ("cuit", int(rec.company_id.vat.replace('AR', ''))),
                        ("ptoVta", rec.point_of_sale),
                        ("tipoCmp", int(rec.afip_document_class_id)),
                        ("nroCmp", int(rec.document_number.split('-')[2])),
                        ("importe", float(rec.amount_total)),
                        ("moneda", str('ARS')),
                        ("ctz", rec.currency_rate),
                        ("tipoDocRec", int(rec.partner_id.document_type_id.afip_code)),
                        ("nroDocRec", int(rec.partner_id.document_number)),
                        ("tipoCodAut", str('E')),
                        ("codAut", int(rec.afip_auth_code))
                    ])
                except:
                    dict_invoice = 'ERROR'
                    pass
                res = json.dumps(dict_invoice, separators=(',', ':'))
            else:
                res = 'N/A'
            rec.json_qr = res
            enc = res.encode('utf-8')
            b64 = base64.encodestring(enc).decode('utf-8').strip()
            rec.texto_modificado_qr = 'https://www.afip.gob.ar/fe/qr/?p=' + str(b64)
            rec.image_qr = base64.b64encode(requests.get(self.env['ir.config_parameter'].get_param('web.base.url') + '/report/barcode/?type=QR&value=' + 'https://www.afip.gob.ar/fe/qr/?p=' + str(b64) + '&width=180&height=180').content)
            print(rec.image_qr)
    json_qr = fields.Char("JSON QR AFIP", compute=_compute_json_qr)
    texto_modificado_qr = fields.Char('Texto Modificado QR', compute=_compute_json_qr)
    image_qr = fields.Binary('QR Imagen', compute=_compute_json_qr)
            
