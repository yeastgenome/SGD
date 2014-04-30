from datetime import datetime
import json
import logging
import uuid

from mpmath import ceil
from pyramid.response import Response
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from zope.sqlalchemy import ZopeTransactionExtension

from src.sgd.backend.backend_interface import BackendInterface
from src.sgd.go_enrichment import query_batter
from src.sgd.model import perf


__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class PerfBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}
                
        perf.Base = declarative_base(cls=Base)

        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        perf.Base.metadata.bind = engine
        
        self.log = set_up_logging(log_directory, 'perf')
        
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name, request):
        request_id = str(uuid.uuid4())
        callback = None if 'callback' not in request.GET else request.GET['callback']
        self.log.info(request_id + ' ' + method_name + ('' if 'identifier' not in request.matchdict else ' ' + request.matchdict['identifier']))
        def f(data):
            self.log.info(request_id + ' end')
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        from src.sgd.model.perf.core import Bioentity
        return get_all(Bioentity, 'json', min_id, max_id)
    
    def bioentity_list(self, bioent_ids):
        from src.sgd.model.perf.core import Bioentity
        return get_list(Bioentity, 'json', bioent_ids)
    
    #Locus
    def locus(self, identifier):
        from src.sgd.model.perf.core import Bioentity
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'json', bioent_id)
    
    def locustabs(self, identifier):
        from src.sgd.model.perf.core import Bioentity
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'locustabs_json', bioent_id)
    
    def all_locustabs(self, min_id, max_id):
        from src.sgd.model.perf.core import Bioentity
        return get_all(Bioentity, 'locustabs_json', min_id, max_id)
    
    #Bioconcept
    def all_bioconcepts(self, min_id, max_id, callback=None):
        from src.sgd.model.perf.core import Bioconcept
        return get_all(Bioconcept, 'json', min_id, max_id)
    
    def bioconcept_list(self, biocon_ids, callback=None):
        from src.sgd.model.perf.core import Bioconcept
        return get_list(Bioconcept, 'json', biocon_ids)
    
    #Reference
    def reference(self, identifier, are_ids=False):
        from src.sgd.model.perf.core import Reference
        if are_ids:
            ref_id = identifier
        else:
            ref_id = get_obj_id(str(identifier).upper(), class_type='REFERENCE')
        return str(get_obj(Reference, 'json', ref_id))

    def author(self, identifier):
        from src.sgd.model.perf.core import Author
        auth_id = get_obj_id(str(identifier), class_type='AUTHOR')
        return get_obj(Author, 'json', auth_id)

    def all_authors(self, min_id, max_id, callback=None):
        from src.sgd.model.perf.core import Author
        return get_all(Author, 'json', min_id, max_id)

    def author_references(self, identifier, are_ids=False):
        if are_ids:
            auth_id = identifier
        else:
            auth_id = get_obj_id(str(identifier).lower(), class_type='AUTHOR')
        return get_author_details(auth_id, 'REFERENCE')

    def all_references(self, min_id, max_id):
        from src.sgd.model.perf.core import Reference
        return get_all(Reference, 'json', min_id, max_id)

    def all_bibentries(self, min_id, max_id):
        from src.sgd.model.perf.core import Reference
        return get_all(Reference, 'bibentry_json', min_id, max_id)
    
    def reference_list(self, reference_ids):
        from src.sgd.model.perf.core import Reference
        return get_list(Reference, 'bibentry_json', reference_ids)
    
    #Interaction
    def interaction_overview(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'INTERACTION')
    
    def interaction_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'INTERACTION')
        if reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'INTERACTION')
        return None
    
    def interaction_graph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'INTERACTION')
    
    def interaction_resources(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_resources(bioent_id, 'INTERACTION')
    
    #Literature
    def literature_overview(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'LITERATURE')
    
    def literature_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'LITERATURE')
        if reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'LITERATURE')
        return None
    
    def literature_graph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'LITERATURE')

    #GO
    def go_enrichment(self, bioent_ids, callback=None):
        from src.sgd.model.perf.core import Bioentity, Bioconcept
        bioent_format_names = []
        num_chunks = ceil(1.0*len(bioent_ids)/500)
        for i in range(num_chunks):
            bioent_format_names.extend([json.loads(x.json)['format_name'] for x in DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids[i*500:(i+1)*500])).all()])
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []
        
        for enrichment_result in enrichment_results:
            identifier = 'GO:' + str(int(enrichment_result[0][3:])).zfill(7)
            goterm_id = get_obj_id(str(identifier).upper(), 'BIOCONCEPT', 'GO')
            goterm = json.loads(get_obj(Bioconcept, 'json', goterm_id))
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        return json.dumps(json_format)

    def go(self, identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = identifier
        else:
            biocon_id = get_obj_id(str(identifier).upper() if str(identifier).upper().startswith('GO') else str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_obj(Bioconcept, 'json', biocon_id)

    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'GO')
        elif go_identifier is not None:
            if are_ids:
                biocon_id = go_identifier
            else:
                biocon_id = get_obj_id(str(go_identifier).upper() if str(go_identifier).upper().startswith('GO') else str(go_identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
            if with_children:
                return get_bioconcept_details(biocon_id, 'LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_details(biocon_id, 'LOCUS')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'GO')

    def go_graph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'GO')

    def go_ontology_graph(self, identifier, are_ids=False):
        if are_ids:
            biocon_id = identifier
        else:
            biocon_id = get_obj_id(str(identifier).upper() if str(identifier).upper().startswith('GO') else str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_bioconcept_graph(biocon_id, 'ONTOLOGY')

    def go_overview(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'GO')

    #Phenotype
    def phenotype(self, identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = identifier
        else:
            biocon_id = get_obj_id(str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return get_obj(Bioconcept, 'json', biocon_id)

    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'PHENOTYPE')
        elif phenotype_identifier is not None:
            if are_ids:
                biocon_id = phenotype_identifier
            else:
                biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            if with_children:
                return get_bioconcept_details(biocon_id, 'LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_details(biocon_id, 'LOCUS')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'PHENOTYPE')
        elif chemical_identifier is not None:
            if are_ids:
                chem_id = chemical_identifier
            else:
                chem_id = get_obj_id(str(chemical_identifier).lower(), class_type='CHEMICAL')
            return get_chemical_details(chem_id, 'PHENOTYPE')

    def phenotype_ontology(self):
        return get_ontology('PHENOTYPE')

    def phenotype_graph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'PHENOTYPE')

    def phenotype_ontology_graph(self, identifier, are_ids=False):
        if are_ids:
            biocon_id = identifier
        else:
            biocon_id = get_obj_id(str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return get_bioconcept_graph(biocon_id, 'ONTOLOGY')

    def phenotype_overview(self, locus_identifier=None, phenotype_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_overview(bioent_id, 'PHENOTYPE')
        elif phenotype_identifier is not None:
            if are_ids:
                biocon_id = phenotype_identifier
            else:
                biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            return get_bioconcept_overview(biocon_id, 'PHENOTYPE')

    def phenotype_resources(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_resources(bioent_id, 'PHENOTYPE')

    #Chemical
    def chemical(self, identifier, are_ids=False):
        from src.sgd.model.perf.core import Chemical
        if are_ids:
            chem_id = identifier
        else:
            chem_id = get_obj_id(str(identifier).lower(), class_type='CHEMICAL')
        return get_obj(Chemical, 'json', chem_id)

    def all_chemicals(self, min_id, max_id, callback=None):
        from src.sgd.model.perf.core import Chemical
        return get_all(Chemical, 'json', min_id, max_id)
    
    #Protein
    def protein_domain_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'DOMAIN')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'DOMAIN')
    
    def regulation_overview(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'REGULATION')
    
    def regulation_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'REGULATION')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'REGULATION')
    
    def regulation_graph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'REGULATION')
    
    def regulation_target_enrichment(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_enrichment(bioent_id, 'REGULATION_TARGET')

    def regulation_paragraph(self, identifier, are_ids=False):
        if are_ids:
            bioent_id = identifier
        else:
            bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_paragraph(bioent_id, 'REGULATION')
    
    #Binding
    def binding_site_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'BINDING')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_bioentity_details(ref_id, 'BINDING')

    #Misc
    def all_disambigs(self, min_id, max_id):
        from src.sgd.model.perf.core import Disambig
        query = DBSession.query(Disambig)
        if min_id is not None:
            query = query.filter(Disambig.id >= min_id)
        if max_id is not None:
            query = query.filter(Disambig.id < max_id)
        disambigs = query.all()
        return json.dumps([{'id': disambig.id,
                            'disambig_key': disambig.disambig_key,
                            'class_type': disambig.class_type,
                            'subclass_type': disambig.subclass_type,
                            'identifier': disambig.obj_id} 
                        for disambig in disambigs]) 
        
#Useful methods

#Get obj/obj_id
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    from src.sgd.model.perf.core import Disambig
    
    if identifier is None:
        return None
    query = DBSession.query(Disambig).filter(func.lower(Disambig.disambig_key)==func.lower(str(identifier)))
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    if len(disambigs) > 0:
        return [(disambig.obj_id, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

def get_obj_id(identifier, class_type=None, subclass_type=None):
    objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
    obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
    return obj_id

def get_all(cls, col_name, min_id, max_id):
    query = DBSession.query(cls)
    if min_id is not None:
        query = query.filter(cls.id >= min_id)
    if max_id is not None:
        query = query.filter(cls.id < max_id)
    objs = query.all()
        
    return '[' + ', '.join(filter(None, [getattr(obj, col_name) for obj in objs])) + ']'

def get_list(cls, col_name, obj_ids):
    num_chunks = ceil(1.0*len(obj_ids)/500)
    objs = []
    for i in range(num_chunks):
        objs.extend(DBSession.query(cls).filter(cls.id.in_(obj_ids[i*500:(i+1)*500])).all())
    return '[' + ', '.join([getattr(obj, col_name) for obj in objs]) + ']'
            
def get_obj(cls, col_name, obj_id):
    if obj_id is not None:
        biocon = DBSession.query(cls).filter(cls.id == obj_id).first()
        return None if biocon is None else getattr(biocon, col_name)
    return None

def get_ontology(class_type):
    from src.sgd.model.perf.core import Ontology
    if class_type is not None:
        ontology = DBSession.query(Ontology).filter(Ontology.class_type == class_type).first()
        return None if ontology is None else ontology.json
    return None

#Get bioentity data

def get_bioentity_overview(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityOverview
    if bioentity_id is not None:
        data = DBSession.query(BioentityOverview).filter(BioentityOverview.bioentity_id == bioentity_id).filter(BioentityOverview.class_type == class_type).first()
        return None if data is None else data.json
    return None
        
def get_bioentity_graph(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityGraph
    if bioentity_id is not None:
        data = DBSession.query(BioentityGraph).filter(BioentityGraph.bioentity_id == bioentity_id).filter(BioentityGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_resources(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityResources
    if bioentity_id is not None:
        data = DBSession.query(BioentityResources).filter(BioentityResources.bioentity_id == bioentity_id).filter(BioentityResources.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_enrichment(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityEnrichment
    if bioentity_id is not None:
        data = DBSession.query(BioentityEnrichment).filter(BioentityEnrichment.bioentity_id == bioentity_id).filter(BioentityEnrichment.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_paragraph(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityParagraph
    if bioentity_id is not None:
        data = DBSession.query(BioentityParagraph).filter(BioentityParagraph.bioentity_id == bioentity_id).filter(BioentityParagraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_details(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityDetails
    if bioentity_id is not None:
        data = DBSession.query(BioentityDetails).filter(BioentityDetails.bioentity_id == bioentity_id).filter(BioentityDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get bioconcept data

def get_bioconcept_graph(bioconcept_id, class_type):
    from src.sgd.model.perf.bioconcept_data import BioconceptGraph
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptGraph).filter(BioconceptGraph.bioconcept_id == bioconcept_id).filter(BioconceptGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioconcept_details(bioconcept_id, class_type):
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptDetails).filter(BioconceptDetails.bioconcept_id == bioconcept_id).filter(BioconceptDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioconcept_overview(bioconcept_id, class_type):
    from src.sgd.model.perf.bioconcept_data import BioconceptOverview
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptOverview).filter(BioconceptOverview.bioconcept_id == bioconcept_id).filter(BioconceptOverview.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get reference data

def get_reference_details(reference_id, class_type):
    from src.sgd.model.perf.reference_data import ReferenceDetails
    if reference_id is not None:
        data = DBSession.query(ReferenceDetails).filter(ReferenceDetails.reference_id == reference_id).filter(ReferenceDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get chemical data

def get_chemical_details(chemical_id, class_type):
    from src.sgd.model.perf.chemical_data import ChemicalDetails
    if chemical_id is not None:
        data = DBSession.query(ChemicalDetails).filter(ChemicalDetails.chemical_id == chemical_id).filter(ChemicalDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get author data

def get_author_details(author_id, class_type):
    from src.sgd.model.perf.author_data import AuthorDetails
    if author_id is not None:
        data = DBSession.query(AuthorDetails).filter(AuthorDetails.author_id == author_id).filter(AuthorDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

def set_up_logging(log_directory, label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.ERROR)
    log = logging.getLogger(label)

    if log_directory is not None:
        hdlr = logging.FileHandler(log_directory + '/' + label + '.' + str(datetime.now().date()) + '.txt')
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        hdlr.setFormatter(formatter)
    else:
        hdlr = logging.NullHandler()
    log.addHandler(hdlr)
    log.setLevel(logging.INFO)
    log.propagate = False
    return log