'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Regulationevidence
from sgdbackend_query import get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_interactions
from sgdbackend_query.query_paragraph import get_paragraph
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_reference, \
    id_to_experiment, id_to_strain, id_to_source
from sgdbackend_utils.obj_to_json import paragraph_to_json, condition_to_json
 
'''
-------------------------------Overview---------------------------------------
'''
def make_overview(bioent_id):
    overview = {}
    paragraph = get_paragraph(bioent_id, 'REGULATION')
    if paragraph is not None:
        overview['paragraph'] = paragraph_to_json(paragraph)
    interactions = get_interactions('REGULATION', bioent_id)
    target_count = len([interaction.bioentity2_id for interaction in interactions if interaction.bioentity1_id==bioent_id])
    regulator_count = len([interaction.bioentity1_id for interaction in interactions if interaction.bioentity2_id==bioent_id])
    
    overview['target_count'] = target_count
    overview['regulator_count'] = regulator_count
    return overview
   
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_details(divided, bioent_id):
    regevidences = get_evidence(Regulationevidence, bioent_id=bioent_id)
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in regevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
            
    tables = {}

    if divided:
        target_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity1_id==bioent_id]
        regulator_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity2_id==bioent_id]
        
        tables['targets'] = create_simple_table(target_regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        tables['regulators'] = create_simple_table(regulator_regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    else:
        tables = create_simple_table(regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables    

def minimize_bioent_json(bioent_json):
    if bioent_json is not None:
        return {'display_name': bioent_json['display_name'],
            'format_name': bioent_json['format_name'],
            'link': bioent_json['link']}
    return None
    
def minimize_reference_json(ref_json):
    if ref_json is not None:
        return {'display_name': ref_json['display_name'],
            'link': ref_json['link']}
    return None
    
def minimize_strain_json(strain_json):
    if strain_json is not None:
        return {'display_name': strain_json['display_name'],
            'link': strain_json['link']}
    return None
    
def minimize_experiment_json(exp_json):
    if exp_json is not None:
        return {'display_name': exp_json['display_name'],
            'link': exp_json['link']}
    return None

def make_evidence_row(regevidence, id_to_conditions): 
    reference_id = regevidence.reference_id 
    experiment_id = regevidence.experiment_id
    strain_id = regevidence.strain_id
    
    conditions = None if regevidence.id not in id_to_conditions else ';'.join(condition_to_json(x) for x in id_to_conditions[regevidence.id])
        
    return {'bioent1': minimize_bioent_json(id_to_bioent[regevidence.bioentity1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[regevidence.bioentity2_id]),
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'source': id_to_source[regevidence.source_id],
                'conditions': conditions
                }

'''
-------------------------------Graph---------------------------------------
'''  

def create_regulation_node(bioent_id, bioent_name, bioent_link, is_focus, total_ev_count, class_type):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent_id), 'name':bioent_name, 'link': bioent_link, 
                    'sub_type':sub_type, 'evidence': total_ev_count, 'class_type': class_type}}

def create_regulation_edge(interaction_id, bioent1_id, bioent2_id, total_ev_count):
    return {'data':{'source': 'Node' + str(bioent1_id), 'target': 'Node' + str(bioent2_id), 'evidence': total_ev_count}}
    
def make_graph(bioent_id):
    regulation_families = get_regulation_family(bioent_id)
    
    id_to_node = {}
    edges = []
    min_evidence_count = None
    max_evidence_count = 0
    max_target_count = 0
    max_regulator_count = 0
    bioent_id_to_evidence_count = {}
    bioent_id_to_class = {}
    
    for regulation_family in regulation_families:
        evidence_count = regulation_family.evidence_count
           
        bioent1_id = regulation_family.bioentity1_id
        bioent2_id = regulation_family.bioentity2_id
        if bioent1_id==bioent_id or bioent2_id==bioent_id:
            if min_evidence_count is None or evidence_count < min_evidence_count:
                min_evidence_count = evidence_count
            if evidence_count > max_evidence_count:
                max_evidence_count = evidence_count
            
            if bioent1_id==bioent_id and evidence_count > max_target_count:
                max_target_count = evidence_count
            if bioent2_id==bioent_id and evidence_count > max_regulator_count:
                max_regulator_count = evidence_count
            
            if bioent1_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent1_id] = evidence_count
            else:
                bioent_id_to_evidence_count[bioent1_id] = max(bioent_id_to_evidence_count[bioent1_id], evidence_count)
                
            if bioent2_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent2_id] = evidence_count
            else:
                bioent_id_to_evidence_count[bioent2_id] = max(bioent_id_to_evidence_count[bioent2_id], evidence_count)
                
            bioent_id_to_class[bioent1_id] = 'REGULATOR'
            bioent_id_to_class[bioent2_id] = 'TARGET'
                                            
    for regulation_family in regulation_families:
        bioent1_id = regulation_family.bioentity1_id
        bioent2_id = regulation_family.bioentity2_id
    
        if bioent1_id not in id_to_node:
            bioent1 = id_to_bioent[bioent1_id]
            evidence_count = bioent_id_to_evidence_count[bioent1_id]
            class_type = bioent_id_to_class[bioent1_id]
            id_to_node[bioent1_id] = create_regulation_node(bioent1_id, bioent1['display_name'], 
                                                            bioent1['link'], bioent1_id==bioent_id, evidence_count, class_type=class_type)
        if bioent2_id not in id_to_node:
            bioent2 = id_to_bioent[bioent2_id]
            evidence_count = bioent_id_to_evidence_count[bioent2_id]
            class_type = bioent_id_to_class[bioent2_id]
            id_to_node[bioent2_id] = create_regulation_node(bioent2_id, bioent2['display_name'], 
                                                            bioent2['link'], bioent2_id==bioent_id, evidence_count, class_type=class_type)
        edges.append(create_regulation_edge(regulation_family.id, bioent1_id, bioent2_id, 
                                             regulation_family.evidence_count))
            
    
    return {'nodes': id_to_node.values(), 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_count,
            'max_target_cutoff': max_target_count, 'max_regulator_cutoff': max_regulator_count}

