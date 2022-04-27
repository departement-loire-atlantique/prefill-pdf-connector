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

    @endpoint()
    def info(self, request):
        return{'hello' : 'Bonjour Prefill'}
        
    @endpoint()
    def clear_ws_json(self, request):
        return {}
    
    @endpoint(
        name="prefill",
        methods=["post"],
        description=ugettext_lazy("Appel de remplissage de PDF"),
    )
    def prefill(self, request, *args, **kwargs):
        self.logger.info(f"DEBUG prefill")
        try:
            payload = json_loads(request.body)      #recupère les données du formulaire Publik rempli
        except (ValueError,):
            raise APIError('Invalid payload format: json expected')

        xfdf_data = render_to_string('data.xfdf', payload.get('fields'))    # remplace les variables de data.xfdf par les bonnes valeurs des données
        self.logger.info(f"xfdf_data : {xfdf_data}")    #logout du webservice

        filename = 'cerfa_10072-02.pdf'
        filename_path = os.path.join(template_dir, filename)
        filled_pdf = utils.fill_form(filename_path, xfdf_data=xfdf_data, tmp_dir=tmp_dir)
        # Serialize in JSON a base64 encoded data
        # https://stackoverflow.com/a/37239382
        self.logger.info(f"filled_pdf : {filled_pdf}")
        with open(filled_pdf, 'rb') as open_file:
            byte_content = open_file.read()
        base64_bytes = base64.b64encode(byte_content)
        # base64_string = base64_bytes.decode('utf-8')
        # base64_string = base64_bytes.decode('ascii')
        file_payload = {}
        file_payload['file'] = {'content_type': 'application/pdf', 'filename': 'cerfa_10072-02_prerempli.pdf'}
        # file_payload['file']['b64_content'] = base64_string
        file_payload['file']['b64_content'] = force_text(base64_bytes, encoding='ascii')

        os.remove(filled_pdf)

        return file_payload