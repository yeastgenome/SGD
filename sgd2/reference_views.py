'''
Created on Feb 21, 2013

@author: kpaskov
'''
from jsonify.large import reference_large, bioent_biocon_small, biorel_small
from jsonify.mini import reference_mini
from model_new_schema.evidence import Phenoevidence, Interevidence
from model_new_schema.reference import Reference
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_phenotype_table_for_reference, \
    create_interaction_table_for_reference
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload
 
 
def get_reference(ref_id):
    reference = None
    try:
        float(ref_id)
        reference = DBSession.query(Reference).filter(Reference.pubmed_id == ref_id).first() 
        if reference is None:
            reference = DBSession.query(Reference).filter(Reference.id == ref_id).first()
    except:
        pass
    if reference is None:
        reference = DBSession.query(Reference).filter(Reference.dbxref_id == ref_id).first() 
    if reference is None:
        print 'REFERENCE IS NONE'
    else:
        print reference_mini(reference)['link']
    return reference
        

@view_config(route_name='reference', renderer='templates/reference.pt')
def reference_view(request):
    pubmed_id = request.matchdict['pubmed_id']
    reference = get_reference(pubmed_id)
    
    json_reference = reference_large(reference)
    return {'layout': site_layout(), 'page_title': 'PMID ' + json_reference['basic_info']['pubmed_id'], 'ref': json_reference}

@view_config(route_name='reference_phenotypes', renderer='json')
def reference_phenotypes_view(request):
    pubmed_id = request.matchdict['pubmed_id']
    reference = get_reference(pubmed_id)

    phenoevidences = DBSession.query(Phenoevidence).options(joinedload('bioent_biocon_evidences'), joinedload('bioent_biocon_evidences.bioent_biocon'), joinedload('bioent_biocon_evidences.bioent_biocon.bioentity'), joinedload('bioent_biocon_evidences.bioent_biocon.bioconcept')).filter(Phenoevidence.reference_id==reference.id).all()
    bioent_biocons = set(phenoevidence.bioent_biocon for phenoevidence in phenoevidences)
    bioent_biocon_jsons = [bioent_biocon_small(bioent_biocon) for bioent_biocon in bioent_biocons]
    return create_phenotype_table_for_reference(bioent_biocon_jsons)

@view_config(route_name='reference_interactions', renderer='json')
def reference_interactions_view(request):
    pubmed_id = request.matchdict['pubmed_id']
    reference = get_reference(pubmed_id)
  
    interevidences = DBSession.query(Interevidence).options(joinedload('biorel_evidence'), joinedload('biorel_evidence.biorel')).filter(Interevidence.reference_id==reference.id).all()
    interactions = set(interevidence.biorel for interevidence in interevidences)
    interaction_jsons = [biorel_small(interaction) for interaction in interactions]
    return create_interaction_table_for_reference(interaction_jsons)