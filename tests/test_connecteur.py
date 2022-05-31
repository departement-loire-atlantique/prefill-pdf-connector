# -*- coding: utf-8 -*-

import pytest
import django_webtest

from django.contrib.contenttypes.models import ContentType
from passerelle_test.models import TestConnector
from passerelle.base.models import ApiUser, AccessRight

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