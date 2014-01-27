'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_core.convert_bioitem import dbxref_type_to_class
from convert_other.convert_auxiliary import convert_bioentity_reference, \
    convert_biofact
from convert_utils import create_or_update, break_up_file, create_format_name
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
import logging
import sys

"""
--------------------- Convert Evidence ---------------------
"""

def create_evidence(old_go_feature, gofeat_id_to_gorefs, goref_id_to_dbxrefs, id_to_bioentity, sgdid_to_bioentity, id_to_reference, key_to_source, 
                    key_to_bioconcept, key_to_bioitem, key_to_gpad_info):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    from model_new_schema.condition import Bioconceptcondition, Bioentitycondition, Bioitemcondition
    evidences = []
        
    go_key = ('GO:' + str(old_go_feature.go.go_go_id), 'GO')
    go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
        
    bioent_id = old_go_feature.feature_id
    bioent = None if bioent_id not in id_to_bioentity else id_to_bioentity[bioent_id]
    if bioent is None:
        print bioent_id
        return []
        
    source = key_to_source[old_go_feature.source]
            
    old_go_refs = [] if old_go_feature.id not in gofeat_id_to_gorefs else gofeat_id_to_gorefs[old_go_feature.id]
    for old_go_ref in old_go_refs:        
        reference_id = old_go_ref.reference_id
        reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    
        qualifier = None
        if old_go_ref.go_qualifier is not None:
            qualifier = old_go_ref.qualifier.replace('_', ' ')
        else:
            aspect = go.go_aspect
            if aspect == 'biological process':
                qualifier = 'involved in'
            elif aspect == 'molecular function':
                qualifier = 'enables'
            elif aspect == 'cellular component':
                qualifier = 'part of'
        conditions = []
            
        old_dbxrefs = [] if old_go_ref.id not in goref_id_to_dbxrefs else goref_id_to_dbxrefs[old_go_ref.id]
        for dbxref in old_dbxrefs:
            dbxref_type = dbxref.dbxref_type
            if dbxref_type == 'GOID':
                go_key = ('GO:' + dbxref.dbxref_id, 'GO')
                cond_go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
                if cond_go is not None:
                    conditions.append(Bioconceptcondition(None, 'With', cond_go))
        
            elif dbxref_type == 'EC number':
                ec_key = (dbxref.dbxref_id, 'EC_NUMBER')
                ec = None if ec_key not in key_to_bioconcept else key_to_bioconcept[ec_key]
                if ec is not None:
                    conditions.append(Bioconceptcondition(None, 'With', ec))
                
            elif dbxref_type == 'DBID Primary':
                sgdid = dbxref.dbxref_id
                cond_bioent = None if sgdid not in sgdid_to_bioentity else sgdid_to_bioentity[sgdid]
                if cond_bioent is not None:
                    conditions.append(Bioentitycondition(None, 'With', cond_bioent))
                
            else:
                bioitem_class_type = dbxref_type_to_class[dbxref_type]
                bioitem_key = (dbxref.dbxref_id, bioitem_class_type)
                bioitem = None if bioitem_key not in key_to_bioitem else key_to_bioitem[bioitem_key]
                if bioitem is not None:
                    conditions.append(Bioitemcondition(None, 'With', bioitem))
                            
        new_evidence = NewGoevidence(source, reference, None, None, bioent, go,
                                old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, conditions,
                                old_go_ref.date_created, old_go_ref.created_by)
        new_conditions = []
        if new_evidence.unique_key() in key_to_gpad_info:
            info = key_to_gpad_info[new_evidence.unique_key()]
            new_evidence.experiment_id = info[0]
            new_conditions = info[1]
        evidences.append((new_evidence, new_conditions))
    return evidences

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    from model_new_schema.evelements import Source as NewSource, Experiment as NewExperiment
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import Bioconcept as NewBioconcept
    from model_new_schema.bioitem import Bioitem as NewBioitem
    from model_new_schema.chemical import Chemical as NewChemical
    from model_old_schema.go import GoFeature as OldGoFeature, GoRef as OldGoRef, GorefDbxref as OldGorefDbxref
    
    log = logging.getLogger('convert.go.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'go_evidence', 'annotation_type', 'qualifier',
                       'bioentity_id', 'bioconcept_id']
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_bioconcept = dict([(x.unique_key(), x) for x in new_session.query(NewBioconcept).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in new_session.query(NewBioitem).all()])
        sgdid_to_bioentity = dict([(x.sgdid, x) for x in id_to_bioentity.values()])
        chebi_id_to_chemical = dict([(x.chebi_id, x) for x in new_session.query(NewChemical).all()])

        uniprot_id_to_bioentity = dict([(x.uniprotid, x) for x in new_session.query(NewBioentity).all()])
        pubmed_id_to_reference = dict([(str(x.pubmed_id), x) for x in new_session.query(NewReference).all()])
        eco_id_to_experiment = dict([(x.eco_id, x) for x in new_session.query(NewExperiment).all()])
        
        gofeat_id_to_gorefs = dict()
        goref_id_to_dbxrefs = dict()
        old_gorefs = old_session.query(OldGoRef).options(joinedload('go_qualifier')).all()
        for old_goref in old_gorefs:
            if old_goref.go_annotation_id in gofeat_id_to_gorefs:
                gofeat_id_to_gorefs[old_goref.go_annotation_id].append(old_goref)
            else:
                gofeat_id_to_gorefs[old_goref.go_annotation_id] = [old_goref]

        old_gorefdbxrefs = old_session.query(OldGorefDbxref).options(joinedload('dbxref')).all()
        for old_gorefdbxref in old_gorefdbxrefs:
            if old_gorefdbxref.goref_id in goref_id_to_dbxrefs:
                goref_id_to_dbxrefs[old_gorefdbxref.goref_id].append(old_gorefdbxref.dbxref)
            else:
                goref_id_to_dbxrefs[old_gorefdbxref.goref_id] = [old_gorefdbxref.dbxref]
            
        key_to_gpad_info = {}    
        for x in break_up_file('data/gp_association.559292_sgd'):
            new_data = create_evidence_from_gpad(x, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_source, eco_id_to_experiment, key_to_bioconcept, 
                              chebi_id_to_chemical, sgdid_to_bioentity)
            if new_data is not None:
                key, info = new_data
                key_to_gpad_info[key] = info
                
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            #Grab all current objects and old objects
            if i < num_chunks-1:
                current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.bioentity_id >= min_id).filter(NewGoevidence.bioentity_id < max_id).all()
            
                old_objs = old_session.query(OldGoFeature).filter(
                                OldGoFeature.feature_id >= min_id).filter(
                                OldGoFeature.feature_id < max_id).all()
                                    
            else:
                current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.bioentity_id >= min_id).all()
            
                old_objs = old_session.query(OldGoFeature).filter(OldGoFeature.feature_id >= min_id).all()
            
            
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            already_seen_obj = set()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, gofeat_id_to_gorefs, goref_id_to_dbxrefs,
                                                     id_to_bioentity, sgdid_to_bioentity, id_to_reference, key_to_source, key_to_bioconcept, key_to_bioitem,
                                                     key_to_gpad_info)
                    
                #Edit or add new objects
                for newly_created_obj, new_conditions in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    if obj_key not in already_seen_obj:
                        obj_id = newly_created_obj.id
                        current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                        current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                        if current_obj_by_key is not None:
                            old_key_to_conditions = dict([((x.format_name, x.class_type), x) for x in current_obj_by_key.conditions])
                            for condition in new_conditions:
                                if (condition.format_name, condition.class_type) not in old_key_to_conditions:
                                    current_obj_by_key.conditions.append(condition)
                                    output_creator.changed(obj_key, 'conditions')
                        
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen_obj.add(obj_key)
                    else:
                        print obj_key
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
    
            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')

def create_evidence_from_gpad(gpad, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_source, eco_id_to_experiment, key_to_bioconcept, 
                              chebi_id_to_chemical, sgdid_to_bioentity):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    from model_new_schema.condition import Bioconceptcondition, Bioentitycondition, Chemicalcondition
    
    if len(gpad) == 1:
        return None
    #db = gpad[0]
    db_object_id = gpad[1]
    qualifier = gpad[2].replace('_', ' ')
    go_id = 'GO:' + str(int(gpad[3][3:]))
    pubmed_id = gpad[4]
    eco_evidence_id = gpad[5]
    #with_field = gpad[6]
    #interacting_taxon_id = gpad[7]
    #date = gpad[8]
    assigned_by = gpad[9]
    annotation_extension = gpad[10].strip()
    annotation_properties = gpad[11].split('|')
    
    if assigned_by != 'SGD':
        return None
        
    go_key = (go_id, 'GO')
    go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
    if go is None:
        print go_key
        
    bioent = None if db_object_id not in uniprot_id_to_bioentity else uniprot_id_to_bioentity[db_object_id]
    if bioent is None:
        print db_object_id
        
    if pubmed_id.startswith('PMID:'):
        reference = None if pubmed_id[5:] not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id[5:]] 
    else:
        return None
    if reference is None:
        print pubmed_id[5:]
        return None
        
    experiment = None if eco_evidence_id not in eco_id_to_experiment else eco_id_to_experiment[eco_evidence_id]
    if experiment is None:
        print eco_evidence_id
         
    source = key_to_source[assigned_by]
    date_created = None
    go_evidence = None
    created_by = None
    annotation_type = None
    note = None
    for annotation_prop in annotation_properties:
        pieces = annotation_prop.split('=')
        if pieces[0] == 'go_evidence':
            go_evidence = pieces[1]
        elif pieces[0] == 'curator_name':
            created_by = pieces[1]
            
    exts = set()
    for x in annotation_extension.split(','):
        for y in x.split('|'):
            if '(' in y:
                exts.add(y)
    conditions = []
    for annotation_ext in exts:
        pieces = annotation_ext.split('(')
        role = pieces[0].replace('_', ' ')
        value = pieces[1][:-1]
        if value.startswith('GO:'):
            go_key = ('GO:' + str(int(value[3:])), 'GO')
            cond_go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
            if cond_go is not None:
                conditions.append(Bioconceptcondition(None, role, cond_go))
    
        elif value.startswith('CHEBI:'):
            chebi_id = value[6:]
            chemical = None if chebi_id not in chebi_id_to_chemical else chebi_id_to_chemical[chebi_id]
            if chemical is not None:
                conditions.append(Chemicalcondition(None, role, chemical, None))
            
        elif value.startswith('SGD:'):
            sgdid = value[4:]
            cond_bioent = None if sgdid not in sgdid_to_bioentity else sgdid_to_bioentity[sgdid]
            if cond_bioent is not None:
                conditions.append(Bioentitycondition(None, role, cond_bioent))
                
        elif value.startswith('UniProtKB:'):
            uniprotid = value[10:]
            cond_bioent = None if uniprotid not in uniprot_id_to_bioentity else uniprot_id_to_bioentity[uniprotid]
            if cond_bioent is not None:
                conditions.append(Bioentitycondition(None, role, cond_bioent))
                
        else:
            print role, value
                
    new_evidence = NewGoevidence(source, reference, experiment, note, bioent, go,
                                go_evidence, annotation_type, qualifier, [],
                                date_created, created_by)
    return new_evidence.unique_key(), (new_evidence.experiment_id, conditions)

"""
--------------------- Convert Paragraph ---------------------
"""

def create_paragraph(gofeature, key_to_bioentity, key_to_source):
    from model_new_schema.paragraph import Paragraph

    format_name = create_format_name(gofeature.feature.name)
    bioentity_key = (format_name, 'LOCUS')

    bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]
    source = key_to_source[gofeature.source]
    date_last_reviewed = gofeature.date_last_reviewed

    if bioentity is not None and source is not None:
        paragraph = Paragraph('GO', source, bioentity, str(date_last_reviewed), gofeature.date_created, gofeature.created_by)
        return [paragraph]
    else:
        return []

def convert_paragraph(old_session_maker, new_session_maker):
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.paragraph import Paragraph
    from model_new_schema.evelements import Source
    from model_old_schema.go import GoFeature as OldGoFeature

    log = logging.getLogger('convert.go.paragraph')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Values to check
        values_to_check = ['text', 'source_id', 'date_created', 'created_by', 'display_name']

        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'GO').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        already_seen = set()

        old_objs = old_session.query(OldGoFeature).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen.add(unique_key)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')

"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    convert_evidence(old_session_maker, new_session_maker, 500)

    convert_paragraph(old_session_maker, new_session_maker)
    
    from model_new_schema.bioconcept import Go
    from model_new_schema.evidence import Goevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Goevidence, 'GO', 'convert.go.bioentity_reference', 10000, get_bioent_ids_f)

    convert_biofact(new_session_maker, Goevidence, Go, 'GO', 'convert.go.biofact', 10000)
            

    

    
            
        
            
            
            
            
            