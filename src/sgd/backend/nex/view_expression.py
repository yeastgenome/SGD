from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.evidence import Bioentitydata
from sqlalchemy.orm import joinedload
import json
from src.sgd.model.nex.auxiliary import Bioentityinteraction
from src.sgd.model.nex.bioentity import Locus
from src.sgd.backend.nex.graph_tools import get_interactions_among
from src.sgd.model.nex.evidence import Expressionevidence
from src.sgd.model.nex.bioitem import Datasetcolumn
from decimal import Decimal
import math

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_expression_evidence(locus_id):
    query = DBSession.query(Bioentitydata)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id).options(joinedload(Bioentitydata.evidence))

    return query.all()

def make_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    expressionevidences = get_expression_evidence(locus_id=locus_id)

    #Expression
    id_to_datasetcolumn = dict([(x.id, x) for x in DBSession.query(Datasetcolumn).options(joinedload(Datasetcolumn.dataset)).all()])
    expression_collapsed = {}
    id_to_dataset = dict()
    dataset_id_to_histogram = dict()
    min_value = 0
    max_value = 0
    for x in expressionevidences:
        value = float(x.value)
        rounded = math.floor(value)
        if value - rounded >= .5:
            rounded += .5

        if rounded < min_value:
            min_value = rounded
        if rounded > max_value:
            max_value = rounded

        rounded = max(-5.5, min(5, rounded))
        if rounded in expression_collapsed:
            expression_collapsed[rounded] += 1
        else:
            expression_collapsed[rounded] = 1

        datasetcolumn = id_to_datasetcolumn[x.evidence.datasetcolumn_id]
        dataset_id = datasetcolumn.dataset_id
        if dataset_id not in id_to_dataset:
            id_to_dataset[dataset_id] = datasetcolumn.dataset
            dataset_id_to_histogram[dataset_id] = set()
        dataset_id_to_histogram[dataset_id].add(rounded)

    datasets = []
    for dataset in id_to_dataset.values():
        obj_json = dataset.to_semi_json()
        obj_json['hist_values'] = sorted(dataset_id_to_histogram[dataset.id])
        datasets.append(obj_json)

    return json.dumps({'overview': expression_collapsed, 'datasets': datasets, 'min_value': min_value, 'max_value': max_value + .5})

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_edge(bioent1_id, bioent2_id, score, class_type, direction):
    return {'data':{'target': 'BIOENTITY' + str(bioent1_id), 'source': 'BIOENTITY' + str(bioent2_id),
            'score':float(score)/10, 'class_type': class_type, 'direction': direction}}

def make_graph(bioent_id):
    id_to_bioentity = dict([(x.id, x) for x in DBSession.query(Locus).all()])
    interactions = DBSession.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION').filter_by(bioentity_id=bioent_id).all()

    if len(interactions) == 0:
         return {'nodes': [], 'edges': [], 'min_coeff': 0, 'max_coeff': 0}
    neighbor_id_to_coeff = dict([(x.interactor_id, x.evidence_count) for x in interactions])

    max_coeff = 0

    coeff_to_interactions = dict()

    for interaction in interactions:
        coeff = interaction.evidence_count
        max_coeff = max_coeff if coeff <= max_coeff else coeff

        if coeff in coeff_to_interactions:
            coeff_to_interactions[coeff].append(interaction)
        else:
            coeff_to_interactions[coeff] = [interaction]

    #Apply 100 node cutoff
    all_neighbors = sorted(neighbor_id_to_coeff.keys(), key=lambda x: neighbor_id_to_coeff[x], reverse=True)
    min_coeff = 0 if len(all_neighbors) <= 50 else neighbor_id_to_coeff[all_neighbors[50]]

    usable_neighbor_ids = [neighbor_id for neighbor_id, coeff in neighbor_id_to_coeff.iteritems() if coeff > min_coeff]
    usable_neighbor_ids.append(bioent_id)
    neighbor_id_to_coeff[bioent_id] = max_coeff


    more_interactions = DBSession.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION').filter(Bioentityinteraction.evidence_count > min_coeff).filter(Bioentityinteraction.bioentity_id.in_(usable_neighbor_ids)).filter(Bioentityinteraction.interactor_id.in_(usable_neighbor_ids)).filter(Bioentityinteraction.bioentity_id < Bioentityinteraction.interactor_id).all()
    for interaction in more_interactions:
        coeff = interaction.evidence_count
        if coeff >= min_coeff:
            if coeff in coeff_to_interactions:
                coeff_to_interactions[coeff].append(interaction)
            else:
                coeff_to_interactions[coeff] = [interaction]

    all_coeffs = sorted(coeff_to_interactions.keys(), reverse=True)

    min_coeff = all_coeffs[0] + 1
    ok_nodes = set()
    ok_interactions = set()

    new_cutoff_index = -1
    new_min_coeff = all_coeffs[0] + 1
    new_nodes = set()
    new_interactions = set()
    while len(ok_interactions) + len(new_interactions) < 100 and new_cutoff_index < len(all_coeffs):
        min_coeff = new_min_coeff
        ok_nodes.update(new_nodes)
        ok_interactions.update(new_interactions)

        new_cutoff_index += 1
        if new_cutoff_index < len(all_coeffs):
            new_min_coeff = all_coeffs[new_cutoff_index]
            new_nodes = set([x for x, y in neighbor_id_to_coeff.iteritems() if y >= new_min_coeff])
            new_interactions = set()
            for coeff, interactions in coeff_to_interactions.iteritems():
                if coeff >= new_min_coeff:
                    new_interactions.update([(min(x.bioentity_id, x.interactor_id), max(x.bioentity_id, x.interactor_id), x.evidence_count, x.direction) for x in interactions if x.bioentity_id in new_nodes and x.interactor_id in new_nodes])
            new_nodes = set([x[0] for x in new_interactions if x[0] not in ok_nodes])
            new_nodes.update([x[1] for x in new_interactions if x[1] not in ok_nodes])
            new_interactions = new_interactions - ok_interactions

    nodes = [create_node(id_to_bioentity[x], x==bioent_id, neighbor_id_to_coeff[x]) for x in ok_nodes]
    edges = [create_edge(x[0], x[1], x[2], 'EXPRESSION', x[3]) for x in ok_interactions]

    return {'nodes': nodes, 'edges': edges, 'min_coeff': float(min_coeff), 'max_coeff': float(max_coeff)}
