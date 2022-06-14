# -*- coding: utf-8 -*-

import mock
import pytest
import django_webtest
import os

# from django.contrib.contenttypes.models import ContentType
# from passerelle_test.models import TestConnector
# from passerelle.base.models import ApiUser, AccessRight

import prefill_pdf.utils as utils
import prefill_pdf.models as models
# from prefill_pdf.models import Prefill_PDF

@pytest.fixture
def app(request):
    # création de l'application Django
    return django_webtest.DjangoTestApp()

@pytest.fixture
def connector(db):
    # création du connecteur et ouverture de la permission "can_access" sans authentification.
    connector = TestConnector.objects.create(slug='test')
    api = ApiUser.objects.create(username='all', keytype='', key='')
    obj_type = ContentType.objects.get_for_model(connector)
    AccessRight.objects.create(
            codename='can_access', apiuser=api,
            resource_type=obj_type, resource_pk=connector.pk)
    return connector

def test_pdftk():
    cmd = "%s" % (utils.PDFTK_PATH)
    output = utils.run_command(cmd)
    assert 'SYNOPSIS' in output

def test_cerfa_existed():
    cerfa_name = 'cerfa_10072-02.pdf'
    cerfa_file = os.path.join(models.template_dir, cerfa_name)
    assert os.path.isfile(cerfa_file)

def test_xfdf_existed():
    xfdf_name = 'data.xfdf'
    xfdf_file = os.path.join(models.template_dir, xfdf_name)
    assert os.path.isfile(xfdf_file)