'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent_biocons, get_biocon, get_bioent, \
    get_phenotype_evidence, get_related_bioent_biocons, get_reference, \
    get_phenotype_evidence_ref, get_biocon_family, get_biocon_biocons
from sgd2.views import site_layout
from utils.utils import create_grouped_evidence_table, create_simple_table, \
    make_reference_list
import math


'''
-------------------------------Views---------------------------------------
'''
@view_config(route_name='phenotype', renderer='templates/phenotype.pt')
def phenotype(request):
    biocon_name = request.matchdict['biocon_name']
    biocon = get_biocon(biocon_name, 'PHENOTYPE')
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    return {'layout': site_layout(), 'page_title': biocon.name, 'biocon': biocon, 'link_maker':LinkMaker(biocon.name, biocon=biocon)} 

@view_config(route_name='phenotype_evidence', renderer='templates/phenotype_evidence.pt')
def phenotype_evidence(request):
    if 'bioent_name' in request.GET:
        #Need a phenotype overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        name = 'Phenotype Evidence for ' + bioent.name
        name_with_link = 'Phenotype Evidence for ' + bioent.name_with_link
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'name_with_link':name_with_link, 'split':True,
                'link_maker':LinkMaker(bioent.name, bioent=bioent)}
    elif 'biocon_name' in request.GET:
        #Need a phenotype overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'PHENOTYPE')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        name = 'Evidence for Phenotype:<br>' + biocon.name
        name_with_link = 'Evidence for Phenotype:<br>' + biocon.name_with_link
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'name_with_link':name_with_link, 'split':False,
                'link_maker':LinkMaker(biocon.name, biocon=biocon)}

    else:
        return Response(status_int=500, body='No Bioent specified.')

@view_config(route_name='phenotype_overview_table', renderer='json')
def phenotype_overview_table(request):
    if 'biocon_name' in request.GET:
        #Need a phenotype overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'PHENOTYPE')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        bioent_biocons = get_bioent_biocons('PHENOTYPE', biocon=biocon)
        phenoevidences = get_phenotype_evidence(bioent_biocons)
        return make_overview_tables(False, phenoevidences) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioent_biocons = get_bioent_biocons('PHENOTYPE', bioent=bioent)
        phenoevidences = get_phenotype_evidence(bioent_biocons)
        return make_overview_tables(True, phenoevidences) 
    
    elif 'reference_name' in request.GET:
        #Need a GO overview table based on a bioent
        ref_name = request.GET['reference_name']
        ref = get_reference(ref_name)
        if ref is None:
            return Response(status_int=500, body='Reference could not be found.')
        phenoevidences = get_phenotype_evidence_ref(ref)
        return make_overview_tables(True, phenoevidences) 

    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')


@view_config(route_name='phenotype_evidence_table', renderer='json')
def phenotype_evidence_table(request):
    if 'biocon_name' in request.GET:
        #Need a phenotype overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'PHENOTYPE')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        bioent_biocons = get_bioent_biocons('PHENOTYPE', biocon=biocon)
        return make_evidence_tables(False, bioent_biocons) 
        
    elif 'bioent_name' in request.GET:
        #Need a phenotype overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioent_biocons = get_bioent_biocons('PHENOTYPE', bioent=bioent)
        return make_evidence_tables(True, bioent_biocons) 
    
    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')
    
@view_config(route_name='phenotype_graph', renderer="json")
def phenotype_graph(request):
    if 'biocon_name' in request.GET:
        #Need a GO graph based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        return create_phenotype_graph(biocon=biocon)
  
    elif 'bioent_name' in request.GET:
        #Need a GO graph based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        return create_phenotype_graph(bioent=bioent)

    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')
    
@view_config(route_name='phenotype_ontology_graph', renderer="json")
def phenotype_ontology_graph(request):
    if 'biocon_name' in request.GET:
        #Need a phenotype ontology graph based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'PHENOTYPE')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        return create_phenotype_ontology_graph(biocon=biocon)

    else:
        return Response(status_int=500, body='No Biocon specified.')

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(divided, phenoevidences):
    tables = {}
            
    if divided:
        divided_evidences = divide_phenoevidences(phenoevidences)
        
        tables['cellular_pheno'] = make_overview_table(divided_evidences['cellular'])
        tables['chemical_pheno'] = make_chemical_overview_table(divided_evidences['chemical'])
        tables['pp_rna_pheno'] = make_pp_rna_overview_table(divided_evidences['pp_rna'])
    else:
        tables['aaData'] = make_overview_table(phenoevidences)
    return tables    

def make_overview_table(phenoevidences):
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in phenoevidences])
    return create_grouped_evidence_table(phenoevidences, evidence_map, make_overview_row) 

def make_chemical_overview_table(phenoevidences):
    evidence_map = dict([(evidence.id, (', '.join([chem.name for chem in evidence.chemicals]), evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in phenoevidences])
    return create_grouped_evidence_table(phenoevidences, evidence_map, make_grouped_overview_row) 

def make_pp_rna_overview_table(phenoevidences):
    evidence_map = dict([(evidence.id, (evidence.reporter, evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in phenoevidences])
    return create_grouped_evidence_table(phenoevidences, evidence_map, make_grouped_overview_row) 

def make_overview_row(bioent_biocon, evs_for_group, group_term):
    bioent = bioent_biocon.bioentity
    biocon = bioent_biocon.bioconcept
    return [biocon.name_with_link, bioent.name_with_link, group_term[1], group_term[2]]

def make_grouped_overview_row(bioent_biocon, evs_for_group, group_term):
    bioent = bioent_biocon.bioentity
    biocon = bioent_biocon.bioconcept
    return [biocon.name_with_link, bioent.name_with_link, group_term[0], group_term[2], group_term[3]]
    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, bioent_biocons):
    tables = {}
    phenoevidences = get_phenotype_evidence(bioent_biocons)

    if divided:
        divided_evidences = divide_phenoevidences(phenoevidences)

        tables['cellular_pheno'] = create_simple_table(divided_evidences['cellular'], make_evidence_row)
        tables['chemical_pheno'] = create_simple_table(divided_evidences['chemical'], make_evidence_row)
        tables['pp_rna_pheno'] = create_simple_table(divided_evidences['pp_rna'], make_evidence_row)
        
    else:
        tables['aaData'] = create_simple_table(phenoevidences, make_evidence_row)
        
    tables['reference'] = make_reference_list(phenoevidences)
        
    return tables    

def make_evidence_row(phenoevidence): 
    bioent = phenoevidence.bioent_biocon.bioentity
    biocon = phenoevidence.bioent_biocon.bioconcept
    reference = ''
    if phenoevidence.reference is not None:
        reference = phenoevidence.reference.name_with_link
     
    allele_entry = ''   
    if phenoevidence.allele:
        allele_entry = phenoevidence.allele.name
                
    chemicals = []
    for chemical in phenoevidence.phenoev_chemicals:
        if chemical.chemical_amt is None:
            chemicals.append(chemical.chemical_name)
        else:
            chemicals.append(chemical.chemical_name + ': ' + chemical.chemical_amt)
    chemical_info = ', '.join(chemicals)
     
    return [biocon.name_with_link, bioent.name_with_link, 
            phenoevidence.qualifier, phenoevidence.experiment_type, phenoevidence.mutant_type, allele_entry,
            phenoevidence.reporter, chemical_info, phenoevidence.strain_id, 
            phenoevidence.source, reference, phenoevidence.description]
    
'''
------------------------------Phenotype Ontology Graph-----------------------------
'''
go_ontology_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'},
                         {'name':'child', 'type':'boolean'},
                         {'name':'direct_gene_count', 'type':'integer'}],
                'edges': [{'name': "directed", 'type': "boolean", 'defValue': True}]}

def create_phenotype_ontology_node(obj, focus_node, child):
    sub_type = 'NORMAL'
    direct_gene_count = obj.direct_gene_count
    if direct_gene_count == 0:
        sub_type = 'NO_GENES'
    if obj == focus_node:
        sub_type = 'FOCUS'
    name = obj.name.replace(' ', '\n')
    size = int(math.ceil(math.sqrt(direct_gene_count)))
    return {'id':'BIOCONCEPT' + str(obj.id), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type, 
            'child':child, 'direct_gene_count':size}

def create_phenotype_ontology_edge(biocon_biocon):
    return { 'id': 'BIOCON_BIOCON' + str(biocon_biocon.id), 'source': 'BIOCONCEPT' + str(biocon_biocon.parent_biocon_id), 'target': 'BIOCONCEPT' + str(biocon_biocon.child_biocon_id)}  

    
def create_phenotype_ontology_graph(biocon):
    
    biocon_family = get_biocon_family(biocon)
    child_ids = biocon_family['child_ids']
    nodes = [create_phenotype_ontology_node(b, biocon, b.id in child_ids) for b in biocon_family['family']]
    edges = [create_phenotype_ontology_edge(e) for e in get_biocon_biocons(biocon_family['all_ids'])]
        
    return {'dataSchema':go_ontology_schema, 'data': {'nodes': nodes, 'edges': edges}, 'has_children':len(child_ids)>0}
 

'''
-------------------------------Graph---------------------------------------
'''  
    
def get_id(bio, observable=None):
    return bio.type + str(bio.id + '_' + observable)

phenotype_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'}],
                'edges': [ { 'name': "label", 'type': "string" }, 
                          {'name':'link', 'type':'string'}]}

def create_phenotype_node(obj, focus_node, observable=None):
    sub_type = obj.type
    if obj == focus_node:
        sub_type = 'FOCUS'
    return {'id':get_id(obj, observable), 'label':obj.name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type}

def create_phenotype_edge(obj, source_obj, sink_obj):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj), 'label': obj.name, 'link':obj.link}  

def create_phenotype_graph(bioent=None, biocon=None): 
    if bioent is not None:
        level_one = set([bioent_biocon for bioent_biocon in get_bioent_biocons('PHENOTYPE', bioent=bioent)])
        level_one = [bioent_biocon for bioent_biocon in level_one if bioent_biocon.bioconcept.phenotype_type=='cellular']

        biocon_ids = [bioent_biocon.biocon_id for bioent_biocon in level_one]
        level_two = set([bioent_biocon for bioent_biocon in get_related_bioent_biocons(biocon_ids)])
    
    usable_bios = set()       
    usable_bios.add(bioent)
    usable_bios.update([bioent_biocon.bioconcept for bioent_biocon in level_one])
    
    bioent_to_edge_count = {}
    for bioent_biocon in level_two:
        ent = bioent_biocon.bioentity
        if ent in bioent_to_edge_count:
            bioent_to_edge_count[ent] = bioent_to_edge_count[ent] + 1
        else:
            bioent_to_edge_count[ent] = 1
       
    more_usable_bios = [bio for bio in bioent_to_edge_count.keys() if bioent_to_edge_count[bio] > 5]
    if len(more_usable_bios) < 150:
        usable_bios.update(more_usable_bios)

         
    nodes = []  
    for usable in usable_bios:
        if usable.type == 'BIOENTITY':
            nodes.append(create_phenotype_node(usable, bioent))
        else:
            nodes.append(create_phenotype_node(usable, bioent))
    
    edges = []
    for bioent_biocon in level_one:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios:
            edges.append(create_phenotype_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept))
    
    for bioent_biocon in level_two:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios and \
        bioent_biocon.bioentity != bioent:
            edges.append(create_phenotype_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept))
    
    return {'dataSchema':phenotype_schema, 'data': {'nodes': nodes, 'edges': edges}}

'''
-------------------------------Utils---------------------------------------
'''  
def divide_phenoevidences(phenoevidences):
    chemical_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioent_biocon.bioconcept.phenotype_type == 'chemical']
    pp_rna_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioent_biocon.bioconcept.phenotype_type == 'pp_rna']
    cellular_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioent_biocon.bioconcept.phenotype_type == 'cellular']
    return {'cellular':cellular_phenoevidences, 'chemical':chemical_phenoevidences, 'pp_rna':pp_rna_phenoevidences}

def divide_bioent_biocons(bioent_biocons):
    chemical_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.phenotype_type == 'chemical']
    pp_rna_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.phenotype_type == 'pp_rna']
    cellular_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.phenotype_type == 'cellular']

    return {'cellular':cellular_bioent_biocons, 'chemical':chemical_bioent_biocons, 'pp_rna':pp_rna_bioent_biocons}
        
