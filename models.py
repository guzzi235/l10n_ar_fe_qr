from openerp import api, fields, models
import base64
from cStringIO import StringIO as StringIO
from collections import OrderedDict
import json
from qrcode import QRCode, constants
from cStringIO import StringIO as StringIO


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # 1. Modificar el campo image_qr a un campo binario
    image_qr = fields.Binary('QR Imagen')

    def _generate_qr_image(self, qr_content):
        qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        output = StringIO()
        img.save(output, format='PNG')
        png_image = output.getvalue()
        output.close()

        return png_image

    @api.multi
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
            b64 = base64.b64encode(enc).decode('utf-8').strip()
            rec.texto_modificado_qr = 'https://www.afip.gob.ar/fe/qr/?p=' + str(b64)

            rec.image_qr = base64.b64encode(rec._generate_qr_image(rec.texto_modificado_qr))
            

    json_qr = fields.Char("JSON QR AFIP", compute=_compute_json_qr)
    texto_modificado_qr = fields.Char('Texto Modificado QR', compute=_compute_json_qr)
    image_qr = fields.Binary('QR Imagen', compute=_compute_json_qr)
