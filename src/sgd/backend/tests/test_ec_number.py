import json
import pytest

from src.sgd.backend.tests import check_evidence, check_obj

__author__ = 'kpaskov'

def test_ec_number_structure(model, identifier='3.4.25.1'):
    response = json.loads(model.ec_number(ec_number_identifier=identifier))
    assert response is not None
    check_obj(response)
    #assert 'count' in response NOT there any more
    #assert 'child_count' in response NOT there any more
    assert 'description' in response
    assert 'class_type' in response
    assert 'format_name' in response
    assert 'display_name' in response

def check_ec_number_evidence(evidence):
    check_evidence(evidence)

def test_ec_number_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.ec_number_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_ec_number_evidence(entry)

def test_ec_number_biocon_details_structure(model, identifier='3.4.25.1'):
    response = json.loads(model.ec_number_details(ec_number_identifier=identifier))
    assert response is not None
    #for entry in response:
    #    check_ec_number_evidence(entry)

