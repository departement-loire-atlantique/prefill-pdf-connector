import os
import base64

from passerelle.base.models import BaseResource
from passerelle.utils.api import endpoint

from passerelle.utils.jsonresponse import APIError
from passerelle.compat import json_loads
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy
from django.utils.encoding import force_bytes, force_text

from . import utils

base_dir = os.path.dirname(__file__)
template_dir = os.path.join(base_dir, 'templates')
tmp_dir = os.path.join(base_dir, 'tmp')

class Prefill_PDF(BaseResource):
    category = 'Divers'

    class Meta:
        verbose_name = 'Pré-remplissage de fichier PDF'

    api_description = "API de remplissage de fichier PDF remplissable avec les données d'un formulaire"

    @endpoint(
        name="info",
        methods=["get"],
        description=ugettext_lazy("Hello world"),
    )
    def info(self, request):
        return{'hello' : 'Bonjour Prefill'}
        
    @endpoint(
        name="clear_ws_json",
        methods=["get"],
        description=ugettext_lazy("Suppression du fichier json de retour d'un appel de webservice pour pouvoir relancer la commande prefill sans erreur")
    )
    def clear_ws_json(self, request):
        return {}
        
    @endpoint(
        name="prefill",
        methods=["post"],
        description=ugettext_lazy("Appel de remplissage de PDF"),
        parameters={
            "stamp_id": {
                "description": "id du fichier tampon .pdf si il existe",
                "exemple_value": "stamp",
                "required": False,
            }
        },
    )
    def prefill(self, request, stamp_id = None):
        self.logger.info(f"DEBUG prefill")
        try:
            payload = json_loads(request.body)      #recupère les données du formulaire Publik rempli
            if stamp_id :
                payload_stamp_content = payload.get('workflow').get('fields').get(stamp_id).get('content')
        except (ValueError,):
            raise APIError('Invalid payload format: json expected')

        xfdf_data = render_to_string('data.xfdf', payload.get('fields'))    # remplace les variables de data.xfdf par les bonnes valeurs des données
        #self.logger.info(f"xfdf_data : {xfdf_data}")    #logout du webservice

        cerfa_name = 'cerfa_10072-02.pdf'
        cerfa_file = os.path.join(template_dir, cerfa_name)
        filled_pdf = utils.fill_form(cerfa_file, xfdf_data=xfdf_data, tmp_dir=tmp_dir)
        # Serialize in JSON a base64 encoded data
        # https://stackoverflow.com/a/37239382
        self.logger.info(f"filled_pdf : {filled_pdf}")

        if stamp_id :
            stamp_file = os.path.join(template_dir,'calque.pdf')
            with open(stamp_file, 'wb') as out_file:
                out_file.write(base64.b64decode(payload_stamp_content))
            self.logger.info(f"stamp file: {stamp_file}")

            stamped_pdf = utils.stamp(filled_pdf, stamp_file, output_pdf_path=tmp_dir)
            self.logger.info(f"stamped_pdf : {stamped_pdf}")
            
            os.remove(stamp_file)
            os.remove(filled_pdf)
        else :
            stamped_pdf = None


        with open(stamped_pdf or filled_pdf, 'rb') as open_file:
            byte_content = open_file.read()
        base64_bytes = base64.b64encode(byte_content)
        os.remove(stamped_pdf or filled_pdf)
        
        file_payload = {}
        file_payload['file'] = {'content_type': 'application/pdf', 'cerfa_name': 'cerfa_10072-02_prerempli_stamped.pdf'}
        file_payload['file']['b64_content'] = force_text(base64_bytes, encoding='ascii')


        return file_payload

