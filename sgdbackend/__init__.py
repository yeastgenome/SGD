import json
import uuid

from backend.backend_interface import BackendInterface
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import model_new_schema
from sgdbackend_utils.cache import get_all_objs, get_objs, get_obj
from sgdbackend_utils.obj_to_json import alias_to_json


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class SGDBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}
                
        model_new_schema.SCHEMA = schema
        model_new_schema.Base = declarative_base(cls=Base)
        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_new_schema.Base.metadata.bind = engine

        from sgdbackend_utils.cache import cache_core
        cache_core()
        
        from sgdbackend_utils import set_up_logging
        self.log = set_up_logging(log_directory, 'sgdbackend')
        
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
        from model_new_schema.bioentity import Bioentity
        return json.dumps([value for key, value in get_all_objs(Bioentity).iteritems() if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    def bioentity_list(self, bioent_ids):
        from model_new_schema.bioentity import Bioentity
        return json.dumps(get_objs(Bioentity, bioent_ids).values())
    
    #Locus
    def locus(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioentity import Bioentity
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(get_obj(Bioentity, locus_id))

    def locus_alias(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioentity import Bioentityalias
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is not None:
            aliases = DBSession.query(Bioentityalias).filter(Bioentityalias.bioentity_id == locus_id).all()
            return json.dumps([alias_to_json(alias) for alias in aliases])
        return None

    def locustabs(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_auxiliary import get_locustabs
        from sgdbackend_utils.obj_to_json import locustab_to_json
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(locustab_to_json(get_locustabs(locus_id)[0]))
    
    def all_locustabs(self, min_id, max_id):
        from sgdbackend_query.query_auxiliary import get_locustabs
        from sgdbackend_utils.obj_to_json import locustab_to_json
        return json.dumps([locustab_to_json(x) for x in get_locustabs(min_id=min_id, max_id=max_id)])

    #Bioconcept
    def all_bioconcepts(self, min_id, max_id):
        from model_new_schema.bioconcept import Bioconcept
        return json.dumps([value for key, value in get_all_objs(Bioconcept) if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    #Chemical
    def chemical(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.chemical import Chemical
        if are_ids:
            chemical_id = identifier
        else:
            chemical_id = get_obj_id(identifier, class_type='CHEMICAL')
        return None if chemical_id is None else json.dumps(get_obj(Chemical, chemical_id))

    def all_chemicals(self, min_id, max_id):
        from model_new_schema.chemical import Chemical
        return json.dumps([value for key, value in get_all_objs(Chemical) if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])

    #Domain
    def domain(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioitem import Bioitem
        if are_ids:
            domain_id = identifier
        else:
            domain_id = get_obj_id(identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        return None if domain_id is None else json.dumps(get_obj(Bioitem, domain_id))

    #ECNumber
    def ec_number(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            ec_number_id = identifier
        else:
            ec_number_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='EC_NUMBER')
        return None if ec_number_id is None else json.dumps(get_obj(Bioconcept, ec_number_id))

    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None, with_children=False, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_ec_number
        from model_new_schema.bioconcept import  Bioconcept
        if are_ids:
            locus_id = locus_identifier
            ec_number_id = ec_number_identifier

            if ec_number_id is not None:
                ec_number = get_obj(Bioconcept, ec_number_id)
                if ec_number is None or ec_number['class_type'] != 'EC_NUMBER':
                    return None
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            phenotype_id = None if ec_number_identifier is None else get_obj_id(ec_number_identifier, class_type='BIOCONCEPT', subclass_type='EC_NUMBER')

        return json.dumps(view_ec_number.make_details(locus_id=locus_id, ec_number_id=ec_number_id, with_children=with_children))

    
    #Reference
    def reference(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        import view_reference
        if are_ids:
            reference_id = identifier
        else:
            reference_id = get_obj_id(identifier, class_type='REFERENCE')
        return None if reference_id is None else json.dumps(view_reference.make_overview(reference_id))
       
    def all_references(self, min_id, max_id):
        from model_new_schema.reference import Reference
        return json.dumps([value for key, value in get_all_objs(Reference).iteritems() if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    def all_bibentries(self, min_id, max_id):
        from sgdbackend_query.query_reference import get_reference_bibs
        return json.dumps([{'id': x.id, 'text': x.text} for x in get_reference_bibs(min_id=min_id, max_id=max_id)])

    def reference_list(self, reference_ids):
        from sgdbackend_query.query_reference import get_reference_bibs
        return json.dumps([{'id': x.id, 'text': x.text} for x in get_reference_bibs(reference_ids=reference_ids)])

    def author(self, identifier, are_ids=False):
        import view_reference
        return json.dumps(view_reference.make_author(identifier))

    def all_authors(self, min_id, max_id):
        from sgdbackend_query.query_reference import get_authors
        return json.dumps(get_authors(min_id, max_id))

    def author_references(self, identifier, are_ids=False):
        import view_reference
        author_json = view_reference.make_author(identifier)
        return None if author_json is None else json.dumps(view_reference.make_author_references(author_json['id']))

    def references_this_week(self, are_ids=False):
        import view_reference
        return json.dumps(view_reference.make_references_this_week())

    #Phenotype
    
    def phenotype(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioconcept import Bioconcept

        import view_phenotype
        if are_ids:
            phenotype_id = identifier
        else:
            phenotype_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        if phenotype_id is None:
            return None
        return None if phenotype_id is None else json.dumps(get_obj(Bioconcept, phenotype_id))

    def phenotype_ontology_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            pheno_id = identifier
            phenotype = get_obj(Bioconcept, pheno_id)
            if phenotype is None or phenotype['class_type'] != 'PHENOTYPE':
                return None
        else:
            pheno_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return None if pheno_id is None else json.dumps(view_phenotype.make_ontology_graph(pheno_id))

    def phenotype_ontology(self):
        from sgdbackend import view_phenotype
        return json.dumps(view_phenotype.make_ontology())
        
    def phenotype_overview(self, locus_identifier=None, phenotype_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            locus_id = locus_identifier
            phenotype_id = phenotype_identifier

            if phenotype_id is not None:
                phenotype = get_obj(Bioconcept, phenotype_id)
                if phenotype is None or phenotype['class_type'] != 'PHENOTYPE':
                    return None
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            phenotype_id = None if phenotype_identifier is None else get_obj_id(phenotype_identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return json.dumps(view_phenotype.make_overview(locus_id=locus_id, phenotype_id=phenotype_id))
    
    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            locus_id = locus_identifier
            phenotype_id = phenotype_identifier
            chemical_id = chemical_identifier
            reference_id = reference_identifier

            if phenotype_id is not None:
                phenotype = get_obj(Bioconcept, phenotype_id)
                if phenotype is None or phenotype['class_type'] != 'PHENOTYPE':
                    return None
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            phenotype_id = None if phenotype_identifier is None else get_obj_id(phenotype_identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            chemical_id = None if chemical_identifier is None else get_obj_id(chemical_identifier, class_type='CHEMICAL')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        
        return json.dumps(view_phenotype.make_details(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children))

    def phenotype_resources(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_misc import get_urls
        from sgdbackend_utils.obj_to_json import url_to_json
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is not None:
            phenotype_resources = get_urls('Phenotype Resources', bioent_id=locus_id)
            mutant_resources = get_urls('Mutant Strains', bioent_id=locus_id)
            phenotype_resources.sort(key=lambda x: x.display_name)
            mutant_resources.sort(key=lambda x: x.display_name)
            return json.dumps({'Phenotype Resources': [url_to_json(url) for url in phenotype_resources],
                               'Mutant Resources': [url_to_json(url) for url in mutant_resources]})
        return None

    def phenotype_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_phenotype.make_graph(locus_id, 'PHENOTYPE'))

    # Go

    def go(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            go_id = identifier
        else:
            go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(get_obj(Bioconcept, go_id))

    def go_ontology_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_go
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            go_id = identifier
            go = get_obj(Bioconcept, go_id)
            if go is None or go['class_type'] != 'GO':
                return None
        else:
            go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(view_go.make_ontology_graph(go_id))
    
    def go_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_go
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_go.make_overview(locus_id))
    
    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_go
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            locus_id = locus_identifier
            go_id = go_identifier
            reference_id = reference_identifier

            if go_id is not None:
                go = get_obj(Bioconcept, go_id)
                if go is None or go['class_type'] != 'GO':
                    return None
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            go_id = None if go_identifier is None else get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_go.make_details(locus_id=locus_id, go_id=go_id, reference_id=reference_id, with_children=with_children))
    
    def go_enrichment(self, bioent_ids):
        from sgdbackend import view_go
        return json.dumps(view_go.make_enrichment(bioent_ids))

    def go_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_phenotype.make_graph(locus_id, 'GO', biocon_f=lambda x: get_obj(Bioconcept, x)['go_aspect'] == 'biological process'))
       
    #Interaction
    def interaction_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_interaction
        from model_new_schema.bioentity import Bioentity
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        locus = get_obj(Bioentity, locus_id)
        return json.dumps(view_interaction.make_overview(locus)) 
    
    def interaction_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_interaction
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_interaction.make_details(locus_id=locus_id, reference_id=reference_id))
        
    def interaction_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_interaction
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_interaction.make_graph(locus_id))
        
    def interaction_resources(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_misc import get_urls
        from sgdbackend_utils.obj_to_json import url_to_json
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is not None:
            resources = get_urls('Interaction Resources', bioent_id=locus_id)
            resources.sort(key=lambda x: x.display_name)
            return json.dumps([url_to_json(url) for url in resources])
        return None

    #Literature
    def literature_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_overview(locus_id))

    def literature_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_literature.make_details(locus_id=locus_id, reference_id=reference_id))
    
    def literature_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        from model_new_schema.bioentity import Bioentity
        if are_ids:
            locus_id = identifier
            locus = get_obj(Bioentity, locus_id)
            if locus is None or locus['class_type'] != 'LOCUS':
                return None
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_graph(locus_id))

    #Protein
    def protein_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_protein
        from model_new_schema.bioentity import Bioentity

        if are_ids:
            locus_id = identifier
            locus = get_obj(Bioentity, locus_id)
            if locus is None or locus['class_type'] != 'LOCUS':
                return None
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_overview(locus_id=locus_id))

    def sequence_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_sequence
        from model_new_schema.bioentity import Bioentity

        if are_ids:
            locus_id = identifier
            locus = get_obj(Bioentity, locus_id)
            if locus is None or locus['class_type'] != 'LOCUS':
                return None
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_sequence.make_overview(locus_id=locus_id))

    def protein_domain_details(self, locus_identifier=None, domain_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_protein
        if are_ids:
            locus_id = locus_identifier
            domain_id = domain_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            domain_id = None if domain_identifier is None else get_obj_id(domain_identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        return None if locus_id is None and domain_id is None else json.dumps(view_protein.make_details(locus_id=locus_id, domain_id=domain_id))

    def protein_domain_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_protein
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_graph(locus_id=locus_id))

    def protein_phosphorylation_details(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_protein
        if are_ids:
            locus_id = identifier
        else:
            locus_id = None if identifier is None else get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_phosphorylation_details(locus_id=locus_id))

    def protein_resources(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_misc import get_urls
        from sgdbackend_utils.obj_to_json import url_to_json
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is not None:
            other = sorted(get_urls('Post-translational modifications', bioent_id=locus_id), key=lambda x: x.display_name)
            homologs = get_urls('Protein Information Homologs', bioent_id=locus_id)
            homologs.extend(get_urls('Analyze Sequence S288C vs. other species', bioent_id=locus_id))
            homologs.sort(key=lambda x: x.display_name)
            protein_databases = sorted(get_urls('Protein databases/Other', bioent_id=locus_id), key=lambda x: x.display_name)
            localization = sorted(get_urls('Localization Resources', bioent_id=locus_id), key=lambda x: x.display_name)
            domain = sorted(get_urls('Domain', bioent_id=locus_id), key=lambda x: x.display_name)
            return json.dumps({'Homologs': [url_to_json(url) for url in homologs],
                               'Protein Databases': [url_to_json(url) for url in protein_databases],
                               'Localization': [url_to_json(url) for url in localization],
                               'Domain': [url_to_json(url) for url in domain],
                               'Other': [url_to_json(url) for url in other]})
        return None

    #Complex
    def complex(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from model_new_schema.bioentity import Bioentity
        if are_ids:
            complex_id = identifier
        else:
            complex_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        return None if complex_id is None else json.dumps(get_obj(Bioentity, complex_id))

    def complex_genes(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_complex

        if are_ids:
            complex_id = identifier
        else:
            complex_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        return None if complex_id is None else json.dumps(view_complex.make_genes(complex_id))

    def complex_details(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_complex

        if are_ids:
            complex_id = identifier
        else:
            complex_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        return None if complex_id is None else json.dumps(view_complex.make_details(complex_id))

    def complex_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_complex, view_phenotype
        from model_new_schema.bioconcept import Bioconcept
        if are_ids:
            complex_id = identifier
        else:
            complex_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        return None if complex_id is None else json.dumps(view_phenotype.make_graph(complex_id, 'GO', bioent_type='COMPLEX', biocon_f=lambda x: get_obj(Bioconcept, x)['go_aspect'] == 'biological process'))


    #Regulation
    def regulation_overview(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_overview(locus_id))

    def regulation_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_regulation.make_details(locus_id=locus_id, reference_id=reference_id))
            
    def regulation_graph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_graph(locus_id))
    
    def regulation_target_enrichment(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        from sgdbackend import view_go
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        target_ids = set([x['bioentity2']['id'] for x in view_regulation.make_details(locus_id=locus_id) if x['bioentity1']['id'] == locus_id])
        if len(target_ids) > 0:
            return json.dumps(view_go.make_enrichment(target_ids))
        else:
            return '[]'

    def regulation_paragraph(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        if are_ids:
            locus_id = identifier
        else:
            locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_paragraph(locus_id))
      
    #Binding
    def binding_site_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_binding
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_binding.make_details(locus_id=locus_id, reference_id=reference_id))

    #Sequence
    def sequence_details(self, locus_identifier=None, contig_identifier=None, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_sequence
        if are_ids:
            locus_id = locus_identifier
            contig_id = contig_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            contig_id = None if contig_identifier is None else get_obj_id(contig_identifier, class_type='SEQUENCE', subclass_type='CONTIG')
        return json.dumps(view_sequence.make_details(locus_id=locus_id, contig_id=contig_id))

    def contig(self, identifier, are_ids=False):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_sequence

        if are_ids:
            contig_id = identifier
        else:
            contig_id = get_obj_id(identifier, class_type='SEQUENCE', subclass_type='CONTIG')
        return None if contig_id is None else json.dumps(view_sequence.make_contig(contig_id))
    
    #Misc
    def all_disambigs(self, min_id, max_id):
        from sgdbackend_query.query_auxiliary import get_disambigs
        from sgdbackend_utils.obj_to_json import disambig_to_json
        return json.dumps([disambig_to_json(x) for x in get_disambigs(min_id, max_id)])
      
            
    
    