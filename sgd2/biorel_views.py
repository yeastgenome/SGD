'''
Created on Feb 21, 2013

@author: kpaskov
'''
from jsonify.large import biorel_large
from jsonify.mini import reference_mini
from jsonify.small import interevidence_small
from model_new_schema.biorelation import Biorelation, BiorelEvidence
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_genetic_evidence_table_for_interaction, \
    create_physical_evidence_table_for_interaction
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload, subqueryload
 
@view_config(route_name='biorel', renderer='templates/biorel.pt')
def biorel_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel = DBSession.query(Biorelation).options(subqueryload('source_bioent'), subqueryload('sink_bioent')).filter(Biorelation.name==biorel_name).first()
    json_biorel = biorel_large(biorel)
    biorel_genetic_evidence_view(request)
    return {'layout': site_layout(), 'page_title': json_biorel['basic_info']['name'], 'biorel': json_biorel}

@view_config(route_name='biorel_genetic_evidence', renderer='json')
def biorel_genetic_evidence_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_id = DBSession.query(Biorelation).filter(Biorelation.name==biorel_name).first().id
    biorel_genetic_evidences = DBSession.query(BiorelEvidence).options(joinedload('evidence'), joinedload('evidence.reference'), joinedload('biorel'), joinedload('evidence.biorel_evidence')).filter(BiorelEvidence.biorel_id==biorel_id).all()
    evidences = set([biorel_evidence.evidence for biorel_evidence in biorel_genetic_evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE' and biorel_evidence.evidence.interaction_type == 'genetic'])
    evidence_jsons = [interevidence_small(evidence) for evidence in evidences]
    return create_genetic_evidence_table_for_interaction(evidence_jsons)

@view_config(route_name='biorel_physical_evidence', renderer='json')
def biorel_physical_evidence_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_id = DBSession.query(Biorelation).filter(Biorelation.name==biorel_name).first().id
    biorel_physical_evidences = DBSession.query(BiorelEvidence).options(joinedload('evidence'), joinedload('evidence.reference'), joinedload('biorel'), joinedload('evidence.biorel_evidence')).filter(BiorelEvidence.biorel_id==biorel_id).all()
    evidences = set([biorel_evidence.evidence for biorel_evidence in biorel_physical_evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE' and biorel_evidence.evidence.interaction_type == 'physical'])
    evidence_jsons = [interevidence_small(evidence) for evidence in evidences]
    return create_physical_evidence_table_for_interaction(evidence_jsons)

@view_config(route_name='biorel_references', renderer='json')
def biorel_references_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_id = DBSession.query(Biorelation).filter(Biorelation.name==biorel_name).first().id
    biorel_evidences = DBSession.query(BiorelEvidence).options(joinedload('evidence'), joinedload('evidence.reference')).filter(BiorelEvidence.biorel_id==biorel_id).all()
    references = set([biorel_evidence.evidence.reference for biorel_evidence in biorel_evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE'])
    json_references = sorted([reference_mini(reference) for reference in references], key=lambda x: x['name'])
    return json_references