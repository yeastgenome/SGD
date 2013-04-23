'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_old_schema.config import DBUSER as OLD_DBUSER
from schema_conversion import check_values, cache, create_or_update, \
    add_or_check
from schema_conversion.old_to_new_bioentity import id_to_bioent
from schema_conversion.output_manager import OutputCreator
import model_old_schema


new_evidence = {}
name_allele = {}
name_chemical = {}
new_phenoevidence_chemical = {}

"""
---------------------Cache------------------------------
"""

id_to_biocon = {}
id_to_evidence = {}
id_to_biocon_biocon = {}
id_to_biocon_ancestor = {}
tuple_to_bioent_biocon = {}
tuple_to_bioent_biocon_evidence = {}

name_to_allele = {}
name_to_chemical = {}
tuple_to_phenoevidence_chemical = {}

def cache_biocon(session, biocon_type):
    from model_new_schema.bioconcept import Bioconcept as NewBiocon
    if biocon_type is None:
        new_entries = dict([(biocon.id, biocon) for biocon in session.query(NewBiocon).all()])
    else:
        new_entries = dict([(biocon.id, biocon) for biocon in session.query(NewBiocon).filter_by(biocon_type=biocon_type).all()])
    id_to_biocon.update(new_entries)
    
def cache_bioent_biocon(session, biocon_type):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    key_extractor = lambda x: (x.bioent_id, x.biocon_id)
    if biocon_type is None:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in session.query(NewBioentBiocon).all()])
    else:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in session.query(NewBioentBiocon).filter_by(biocon_type=biocon_type).all()])
    tuple_to_bioent_biocon.update(new_entries)
    
def cache_evidence(session, evidence_type):
    from model_new_schema.evidence import Evidence as NewEvidence
    if evidence_type is None:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in session.query(NewEvidence).all()])
    else:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in session.query(NewEvidence).filter_by(evidence_type=evidence_type).all()])
    id_to_evidence.update(new_entries)
             

"""
---------------------Create------------------------------
"""

def create_bioent_biocon_name(bioent, biocon):
    return bioent.official_name + '---' + biocon.official_name

"""
------------GO--------------
"""
def create_go_id(old_go_id):
    return old_go_id+87636

def create_goevidence_id(old_evidence_id):
    return old_evidence_id+1322521  
                 
abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go):
    from model_new_schema.bioconcept import Go as NewGo
    
    new_go = NewGo(old_go.go_go_id, old_go.go_term, abbrev_to_go_aspect[old_go.go_aspect], old_go.go_definition, 
                   biocon_id=create_go_id(old_go.id), date_created=old_go.date_created, created_by=old_go.created_by)
    return new_go

def create_go_bioent_biocon(old_go_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
        
    bioent = id_to_bioent[bioent_id]
    biocon = id_to_biocon[biocon_id]
    name = create_bioent_biocon_name(bioent, biocon)
    return NewBioentBiocon(bioent_id, biocon_id, name, biocon.biocon_type)

def create_goevidence(old_go_feature, go_ref):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
    bioent_biocon_id = tuple_to_bioent_biocon[(bioent_id, biocon_id)].id
    evidence_id = create_goevidence_id(go_ref.id)
    qualifier = None
    if go_ref.go_qualifier is not None:
        qualifier = go_ref.qualifier
    return NewGoevidence(bioent_biocon_id, go_ref.reference_id, old_go_feature.go_evidence, old_go_feature.annotation_type, old_go_feature.source,
                                qualifier, old_go_feature.date_last_reviewed, 
                                evidence_id=evidence_id, date_created=go_ref.date_created, created_by=go_ref.created_by)
    
def create_go_biocon_biocon(go_path):
    from model_new_schema.bioconcept import BioconBiocon as NewBioconBiocon
    if go_path.generation == 1:
        parent_id = go_path.ancestor_id
        child_id = go_path.child_id
        relationship_type = go_path.relationship_type
        return NewBioconBiocon(parent_id, child_id, relationship_type, biocon_biocon_id=go_path.id)
    else:
        return None

def create_go_biocon_ancestor(go_path):
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor
    ancestor_id = go_path.ancestor_id
    child_id = go_path.child_id
    return NewBioconAncestor(ancestor_id, child_id, biocon_ancestor_id=go_path.id)

"""
------------Phenotype--------------
"""

def create_phenotype_id(old_phenotype_id):
    return old_phenotype_id

def create_phenoevidence_id(old_evidence_id):
    return old_evidence_id

def create_phenotype(old_phenotype):
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    new_phenotype = NewPhenotype(old_phenotype.observable.title(),
                                 biocon_id=create_go_id(old_phenotype.id), date_created=old_phenotype.date_created, created_by=old_phenotype.created_by)
    return new_phenotype

def create_phenotype_bioent_biocon(old_phenotype_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_phenotype_feature.feature_id
    biocon_id = create_phenotype_id(old_phenotype_feature.go_id)
        
    bioent = id_to_bioent[bioent_id]
    biocon = id_to_biocon[biocon_id]
    name = create_bioent_biocon_name(bioent, biocon)
    return NewBioentBiocon(bioent_id, biocon_id, name, biocon.biocon_type)

def create_allele(old_phenotype_feature):
    from model_new_schema.evidence import Allele as NewAllele
    allele_info = old_phenotype_feature.experiment.allele
    new_allele = NewAllele(allele_info[0], allele_info[1])
    return new_allele

def create_chemical(old_phenotye_feature):
    from model_new_schema.chemical import Chemical as NewChemical
    chemical_info = old_phenotye_feature.experiment.chemical
    new_chemical = NewChemical(chemical_info[0])
    return new_chemical

def create_phenoevidence(old_phenotye_feature):
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    evidence_id = create_phenoevidence_id(old_phenotye_feature.id)
    reference_id = None
    strain_id = None
    allele_id = None
    new_phenoevidence = NewPhenoevidence(old_phenotye_feature.experiment_type, reference_id, strain_id, old_phenotye_feature.mutant_type, 
                                         allele_id, old_phenotye_feature.source, old_phenotye_feature.qualifier, 
                                         old_phenotye_feature.evidence_type, evidence_id, old_phenotye_feature.date_created, old_phenotye_feature.created_by)
    if old_phenotye_feature.experiment is not None:
        experiment = old_phenotye_feature.experiment
        new_phenoevidence.reporter = experiment.reporter[0]
        new_phenoevidence.reporter_desc = experiment.reporter[1]
        new_phenoevidence.strain_id = experiment.strain[0]
        new_phenoevidence.strain_details = experiment.strain[1]
        new_phenoevidence.budding_index = experiment.budding_index
        new_phenoevidence.glutathione_excretion = experiment.glutathione_excretion
        new_phenoevidence.z_score = experiment.z_score
        new_phenoevidence.relative_fitness_score = experiment.relative_fitness_score
        new_phenoevidence.chitin_level = experiment.chitin_level
    
        description_pieces = []
        comment = experiment.experiment_comment
        if comment is not None:
            description_pieces.append('Experiment: ' + comment)
            
        if len(experiment.condition) > 0:
            conditions = []
            for (a, b) in experiment.condition:
                if b is None:
                    conditions.append(a)
                else:
                    conditions.append(a + '- ' + b)
            condition_info = ', '.join(conditions)
            description_pieces.append('Condition: ' + condition_info)
            
        if len(experiment.details) > 0:
            details = []
            for (a, b) in experiment.details:
                if b is None:
                    details.append(a)
                else:
                    details.append(a + '- ' + b)
            detail_info = ', '.join(details)
            description_pieces.append('Details: ' + detail_info)
            
        new_phenoevidence.description = '; '.join(description_pieces)

    return new_phenoevidence    

def create_phenoevidence_chemical(old_phenotype_feature):
    from model_new_schema.evidence import PhenoevidenceChemical as NewPhenoevidenceChemical
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    chemical_info = old_phenotype_feature.experiment.chemical
    if chemical_info is not None:
        chemical_id = name_to_chemical[chemical_info[0]]
        chemical_amount = chemical_info[1]
        new_pheno_chemical = NewPhenoevidenceChemical(evidence_id, chemical_id, chemical_amount)
        return new_pheno_chemical
    return None
    
def create_phenotype_bioent_biocon_evidence(old_phenotype_feature):
    from model_new_schema.bioconcept import BioentBioconEvidence as NewBioentBioconEvidence
    bioent_id = old_phenotype_feature.feature_id
    biocon_id = create_phenotype_id(old_phenotype_feature.phenotype_id)
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    bioent_biocon_id = tuple_to_bioent_biocon[(bioent_id, biocon_id)].id
    return NewBioentBioconEvidence(bioent_biocon_id, evidence_id)

"""
---------------------Add or Check------------------------------
"""

def check_biocon(new_biocon, current_biocon):
    match = check_values(new_biocon, current_biocon, 
                         ['official_name', 'biocon_type', 'date_created', 'created_by'])
    return match

def check_evidence(new_evidence, current_evidence):
    match = check_values(new_evidence, current_evidence, 
                         ['experiment_type', 'reference_id', 'evidence_type', 'strain_id', 'date_created', 'created_by'])
    return match

def add_or_check_bioent_biocon_evidence(new_bioent_biocon_evidence, session, output_creator):
    key = (new_bioent_biocon_evidence.bioent_biocon_id, new_bioent_biocon_evidence.evidence_id)
    if key in tuple_to_bioent_biocon_evidence:
        current_bioent_biocon_evidence = tuple_to_bioent_biocon_evidence[key]
        match = check_values(current_bioent_biocon_evidence, current_bioent_biocon_evidence, 
                         ['bioent_biocon_id', 'evidence_id'])
        if not match:
            output_creator.changed('bioent_biocon_evidence')
    else:
        session.add(new_bioent_biocon_evidence)
        tuple_to_bioent_biocon[key] = new_bioent_biocon_evidence
        output_creator.added('bioent_biocon_evidence')
     
"""
---------------------Convert------------------------------
"""   

def convert_go(old_model, session):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature

    from model_new_schema.bioentity import Bioentity as NewBioentity
      
    output_creator = OutputCreator()

    #Cache bioents
    cache(NewBioentity, id_to_bioent, lambda x: x.id, session, output_creator, 'bioent')
     
    #Cache go_biocons
    cache_biocon(session, 'GO')
    output_creator.cached('biocon')

    #Create new go_biocons if they don't exist, or update the database if they do.
    old_objs = old_model.execute(model_old_schema.model.get(OldGo), OLD_DBUSER)
    key_maker = lambda x: x.id
    values_to_check = ['go_go_id', 'go_term', 'go_aspect', 'go_definition']
    create_or_update(old_objs, id_to_biocon, create_go, key_maker, values_to_check, old_model, session, output_creator, 'go_term', [check_biocon])

    #Cache bioent_biocons
    cache_bioent_biocon(session, 'GO')
    output_creator.cached('bioent_biocon')
    
    #Create new bioent_biocons if they don't exist, or update the database if they do.
    old_go_features = old_model.execute(model_old_schema.model.get(OldGoFeature), OLD_DBUSER)
    key_maker = lambda x: (x.bioent_id, x.biocon_id)
    values_to_check = ['bioent_id', 'biocon_id', 'official_name', 'biocon_type']
    create_or_update(old_go_features, tuple_to_bioent_biocon, create_go_bioent_biocon, key_maker, values_to_check, old_model, session, output_creator, 'bioent_biocon')
    
#    #Cache goevidences
#    cache_evidence(session, 'GO_EVIDENCE')
#    output_creator.cached('goevidence')
#    
#    #Create new goevidences if they don't exist, or update the database if they do.
#    key_maker = lambda x: x.id
#    values_to_check = ['bioent_biocon_id', 'go_evidence', 'annotation_type', 'source', 'date_last_reviewed', 'qualifier']
#    for old_go_feature in old_go_features: 
#        for go_ref in old_go_feature.go_refs:
#            new_evidence = create_goevidence(old_go_feature, go_ref)
#            add_or_check(new_evidence, id_to_evidence, key_maker, values_to_check, session, output_creator, 'goevidence', [check_evidence])
#    output_creator.finished('goevidence')            
#    
#    use_in_graph = set()
#    for goevidence in id_to_evidence.values():
#        if goevidence.evidence_type == 'GO_EVIDENCE' and goevidence.annotation_type != 'computational':
#            use_in_graph.add(goevidence.bioent_biocon)
#    
#    #Set use_in_graph value for all bioent_biocons 
#    changed = 0;
#    for bioent_biocon in tuple_to_bioent_biocon.values():
#        if bioent_biocon.use_in_graph == 'Y' and bioent_biocon not in use_in_graph:
#            bioent_biocon.use_in_graph = 'N'
#            changed = changed + 1
#        elif bioent_biocon.use_in_graph == 'N' and bioent_biocon in use_in_graph:
#            bioent_biocon.use_in_graph = 'Y'
#            changed = changed + 1
#    print 'In total ' + str(changed) + ' bioent_biocons use_in_graph changed.'

#    #Cache biocon_biocons
#    key_maker = lambda x: x.id
#    cache(NewBioconBiocon, id_to_biocon_biocon, key_maker, session, output_creator, 'biocon_biocon')
#    
#    #Create new biocon_biocons if they don't exist, or update the database if they do.
#    old_go_paths = old_model.execute(model_old_schema.model.get(OldGoPath), OLD_DBUSER)
#    values_to_check = ['parent_biocon_id', 'child_biocon_id', 'relationship_type']
#    for old_go_path in old_go_paths: 
#        new_biocon_biocon = create_go_biocon_biocon(old_go_path)
#        add_or_check(new_biocon_biocon, id_to_biocon_biocon, key_maker, values_to_check, session, output_creator, 'biocon_biocon')
#    output_creator.finished('biocon_biocon')  
#    
#    #Cache biocon_ancestors
#    key_maker = lambda x: x.id
#    cache(NewBioconAncestor, id_to_biocon_ancestor, key_maker, session, output_creator, 'biocon_ancestor')
#    
#    #Create new biocon_ancestors if they don't exist, or update the database if they do.
#    values_to_check = ['ancestor_biocon_id', 'child_biocon_id']
#    for old_go_path in old_go_paths: 
#        new_biocon_ancestor = create_go_biocon_ancestor(old_go_path)
#        add_or_check(new_biocon_ancestor, id_to_biocon_ancestor, key_maker, values_to_check, session, output_creator, 'biocon_ancestor')
#    output_creator.finished('biocon_ancestor')      
   
    
            
    
def convert_phenotype(old_session, new_session):
    from model_new_schema.evidence import Allele as NewAllele, PhenoevidenceChemical as NewPhenoevidenceChemical
    from model_new_schema.chemical import Chemical as NewChemical
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import Phenotype as NewPhenotype, BioconBiocon as NewBioconBiocon, BioconAncestor as NewBioconAncestor

    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature, Phenotype as OldPhenotype
    from model_old_schema.cv import CVTerm as OldCVTerm
    
#    output_creator = OutputCreator()

#    #Cache bioents
#    cache(NewBioentity, id_to_bioent, lambda x: x.id, session, output_creator, 'bioent')
#    output_creator.cached('bioent')
#     
#    #Cache phenotype_biocons
#    cache_biocon(session, 'PHENOTYPE')
#    output_creator.cached('biocon')
#
#    #Create new phenotype_biocons if they don't exist, or update the database if they do.
#    old_phenotypes = old_model.execute(model_old_schema.model.get(OldPhenotype), OLD_DBUSER)
#    key_maker = lambda x: x.id
#    values_to_check = ['observable']
#    create_or_update(old_phenotypes, id_to_biocon, create_phenotype, key_maker, values_to_check, old_model, session, output_creator, 'phenotype', [check_biocon])
#
#    #Cache bioent_biocons
#    cache_bioent_biocon(session, 'PHENOTYPE')
#    output_creator.cached('bioent_biocon')
#    
#    #Create new bioent_biocons if they don't exist, or update the database if they do.
#    old_phenotype_features = old_model.execute(model_old_schema.model.get(OldPhenotypeFeature), OLD_DBUSER)
#    key_maker = lambda x: (x.bioent_id, x.biocon_id)
#    values_to_check = ['bioent_id', 'biocon_id', 'official_name', 'biocon_type']
#    create_or_update(old_phenotype_features, tuple_to_bioent_biocon, create_phenotype_bioent_biocon, key_maker, values_to_check, old_model, session, output_creator, 'bioent_biocon')
#    
#    #Cache phenoevidences
#    cache_evidence(session, 'PHENOTYPE_EVIDENCE')
#    output_creator.cached('phenoevidence')
#    
#    #Create new phenoevidences if they don't exist, or update the database if they do.
#    key_maker = lambda x: x.id
#    values_to_check = ['mutant_type', 'mutant_allele_id', 'source', 'qualifier', 'reporter', 'reporter_desc', 'strain_details', 
#                       'budding_index', 'glutathione_excretion', 'z_score', 'relative_fitness_score', 'chitin_level', 'description']
#    create_or_update(old_phenotype_features, id_to_evidence, key_maker, values_to_check, old_model, session, output_creator, 'phenoevidence', [check_evidence])
#    
#    #Cache bioent_biocon_evidences
#    key_maker = lambda x: (x.bioent_biocon_id, x.evidence_id)
#    output_message = 'bioent_biocon_evidence'
#    cache(NewBioentBioconEvidence, tuple_to_bioent_biocon_evidence, key_maker, session, output_creator, output_message)
#    
#    #Create new bioent_biocon_evidences if they don't exist, or update the database if they do.
#    values_to_check = ['bioent_biocon_id', 'evidence_id']
#    create_or_update(old_phenotype_features, tuple_to_bioent_biocon_evidence, create_phenotype_bioent_biocon_evidence, key_maker, values_to_check,
#                     old_model, session, output_creator, output_message)
#    
#    #Cache alleles
#    key_maker = lambda x: x.name
#    output_message = 'allele'
#    cache(NewAllele, name_to_allele, key_maker, session, output_creator, output_message)
#    
#    #Create new alleles if they don't exist, or update the database if they do.
#    values_to_check = ['name', 'description']
#    create_or_update(old_phenotype_features, name_to_allele, create_allele, key_maker, values_to_check, old_model, output_creator, output_message)
#
#    #Cache chemicals
#    key_maker = lambda x: x.name
#    output_message = 'chemical'
#    cache(NewChemical, name_to_chemical, key_maker, session, output_creator, output_message)
#    
#    #Create new chemicals if they don't exist, or update the database if they do.
#    values_to_check = ['name', 'description']
#    create_or_update(old_phenotype_features, name_to_allele, create_allele, key_maker, values_to_check, old_model, output_creator, output_message)
#
#    #Cache evidence_chemical
#    key_maker = lambda x: (x.evidence_id, x.chemical_id)
#    output_message = 'evidence_chemical'
#    cache(NewPhenoevidenceChemical, tuple_to_phenoevidence_chemical, key_maker, session, output_creator, output_message)
#    
#    #Create new evidence_chemical if they don't exist, or update the database if they do.
#    values_to_check = ['evidence_id', 'chemical_id', 'chemical_amt']
#    create_or_update(old_phenotype_features, tuple_to_phenoevidence_chemical, create_phenoevidence_chemical, key_maker, values_to_check, 
#                     old_model, output_creator, output_message)

    #Add definitions to phenotypes
    name_to_phenotype = {}
    phenotype_output_creator = OutputCreator('phenotype')
    #Cache phenotypes
    cache(NewPhenotype, name_to_phenotype, lambda x: x.observable, new_session, phenotype_output_creator)
    cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
    for cv_term in cv_terms:
        new_phenotype = NewPhenotype(cv_term.name, get_phenotype_type(cv_term.name), cv_term.definition)
        values_to_check = ['observable', 'phenotype_type', 
                           'biocon_type', 'official_name', 'description']
        add_or_check(new_phenotype, name_to_phenotype, new_phenotype.observable, values_to_check, new_session, phenotype_output_creator)
    phenotype_output_creator.finished()   
    
#    #Add phenotype ontology
#    for cv_term in cv_terms:
#        child_id = name_to_phenotype[cv_term.name].id
#        for parent in cv_term.parents:
#            parent_id = name_to_phenotype[parent.name].id
#            
#            biocon_biocon = NewBioconBiocon(parent_id, child_id, 'is a')
#            new_session.add(biocon_biocon)
#        
#        parents = list(cv_term.parents)
#        while len(parents) > 0:
#            parent = parents.pop()
#            biocon_ancestor = NewBioconAncestor(name_to_phenotype[parent.name].id, child_id)
#            new_session.add(biocon_ancestor)
#            parents.extend(parent.parents)
        
        
            
    
def get_phenotype_type(observable):
    if observable in {'chemical compound accumulation', 'resistance to chemicals', 'osmotic stress resistance', 'alkaline pH resistance',
                      'ionic stress resistance', 'oxidative stress resistance', 'small molecule transport', 'metal resistance', 
                      'acid pH resistance', 'hyperosmotic stress resistance', 'hypoosmotic stress resistance', 'chemical compound excretion'}:
        return 'chemical'
    elif observable in {'protein/peptide accumulation', 'protein/peptide modification', 'protein/peptide distribution', 
                        'RNA accumulation', 'RNA localization', 'RNA modification'}:
        return 'pp_rna'
    else:
        return 'cellular'
    
            
        
            
            
            
            
            