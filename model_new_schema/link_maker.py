'''
Created on Mar 6, 2013

@author: kpaskov
'''
from string import lower
def add_link(name, link, new_window=False):
    if new_window:
        return '<a href="%s" target="_blank">%s</a>' % (link, name)
    else:
        return '<a href="%s">%s</a>' % (link, name)

link_symbol = '---'

def add_format_name_params(link, key_to_obj):
    params = {}
    for key, obj in key_to_obj.iteritems():
        if obj is not None:
            params[key] = obj.format_name
    full_link = link + '&'.join([key + '=' + value for key, value in params.iteritems()])
    return full_link

class LinkMaker():
    bioent=None
    biocon=None
    biorel=None
    chemical=None
    
    def __init__(self, name, bioent=None, biocon=None, biorel=None, reference=None, chemical=None):
        self.bioent=bioent
        self.biocon=biocon
        self.biorel=biorel
        self.reference=reference
        self.chemical=chemical
    
        #GO links    
        setattr(self, 'go_evidence_link', add_format_name_params('/go_evidence?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'go_overview_table_link', add_format_name_params('/go_overview_table?', {'bioent_name':bioent, 'biocon_name': biocon, 'reference_name':reference}))
        setattr(self, 'go_evidence_table_link', add_format_name_params('/go_evidence_table?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'go_graph_link', add_format_name_params('/go_graph?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'go_ontology_graph_link', add_format_name_params('/go_ontology_graph?', {'biocon_name': biocon}))
   
        setattr(self, 'go_f_filename', name + '_function_go_terms')
        setattr(self, 'go_p_filename', name + '_process_go_terms')
        setattr(self, 'go_c_filename', name + '_component_go_terms')
        setattr(self, 'go_filename', name + '_go_terms')
        
        setattr(self, 'go_f_evidence_filename', name + '_function_go_evidence')
        setattr(self, 'go_p_evidence_filename', name + '_process_go_evidence')
        setattr(self, 'go_c_evidence_filename', name + '_component_go_evidence')
        setattr(self, 'go_evidence_filename', name + '_go_evidence')

        #Phenotype links
        setattr(self, 'phenotype_evidence_link', add_format_name_params('/phenotype_evidence?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'phenotype_overview_table_link', add_format_name_params('/phenotype_overview_table?', {'bioent_name':bioent, 'biocon_name': biocon, 'reference_name':reference, 'chemical_name':chemical}))
        setattr(self, 'phenotype_evidence_table_link', add_format_name_params('/phenotype_evidence_table?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'phenotype_graph_link', add_format_name_params('/phenotype_graph?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'phenotype_ontology_graph_link', add_format_name_params('/phenotype_ontology_graph?', {'biocon_name': biocon}))
    
        setattr(self, 'cellular_phenotype_filename', name + '_cellular_phenotypes')
        setattr(self, 'chemical_phenotype_filename', name + '_chemical_phenotypes')
        setattr(self, 'pp_rna_phenotype_filename', name + '_pp_rna_phenotypes')
        setattr(self, 'phenotype_filename', name + '_phenotypes')
        
        setattr(self, 'cellular_phenotype_evidence_filename', name + '_cellular_pheno_evidence')
        setattr(self, 'chemical_phenotype_evidence_filename', name + '_chemical_pheno_evidence')
        setattr(self, 'pp_rna_phenotype_evidence_filename', name + '_pp_rna_pheno_evidence')
        setattr(self, 'phenotype_evidence_filename', name + '_phenotypes')


        #Interaction links
        setattr(self, 'interaction_evidence_link', add_format_name_params('/interaction_evidence?', {'bioent_name':bioent, 'biocon_name': biocon}))
        setattr(self, 'interaction_overview_table_link', add_format_name_params('/interaction_overview_table?', {'bioent_name':bioent, 'reference_name':reference}))
        setattr(self, 'interaction_evidence_table_link', add_format_name_params('/interaction_evidence_table?', {'bioent_name':bioent, 'biorel_name': biorel}))
        setattr(self, 'interaction_graph_link', add_format_name_params('/interaction_graph?', {'bioent_name':bioent}))
        
        setattr(self, 'interaction_filename', name + '_interactions')
        setattr(self, 'genetic_interaction_filename', name + '_genetic_interactions')
        setattr(self, 'physical_interaction_filename', name + '_physical_interactions')
        
        setattr(self, 'interaction_evidence_filename', name + '_interaction_evidence')
        setattr(self, 'genetic_interaction_evidence_filename', name + '_genetic_interaction_evidence')
        setattr(self, 'physical_interaction_evidence_filename', name + '_physical_interaction_evidence')
        
        #Litguide links
        setattr(self, 'bioent_evidence_link', add_format_name_params('/bioent_evidence?', {'bioent_name':bioent, 'reference_name': reference}))
        setattr(self, 'bioent_overview_table_link', add_format_name_params('/bioent_overview_table?', {'bioent_name':bioent, 'reference_name': reference}))
        setattr(self, 'bioent_evidence_table_link', add_format_name_params('/bioent_evidence_table?', {'bioent_name':bioent}))
        setattr(self, 'bioent_filename', name + '_litguide')
        setattr(self, 'bioent_evidence_filename', name + '_litguide_evidence')

        #Sequence links
        setattr(self, 'sequence_link', add_format_name_params('/sequence?', {'bioent_name': bioent}))
        
        #Protein composition filenames
        setattr(self, 'aa_comp_filename', name + '_amino_acid_comp')
        setattr(self, 'atomic_comp_filename', name + 'atomic_comp')
        setattr(self, 'half_life_filename', name + '_half_life')
        setattr(self, 'extinction_coeff_filename', name + '_extinction_coeffs')
        setattr(self, 'coding_region_filename', name + '_coding_region_calcs')
        setattr(self, 'indices_filename', name + '_indices')
    

#Biocon links
def go_link(biocon):
    return '/go/' + biocon.format_name
def phenotype_link(biocon):
    return biocon.format_name
    
#Bioentity links
def bioent_link(bioent):
    return bioent_link_from_basics(bioent.bioent_type, bioent.format_name)
def bioent_link_from_basics(bioent_type, bioent_format_name):
    return '/%s/%s' % (bioent_type.lower(), bioent_format_name)
def bioent_wiki_link(bioent):
    return 'http://wiki.yeastgenome.org/index.php/' + bioent.format_name

#Biorelation links
def interaction_link(biorel):
    return add_format_name_params('/interaction_evidence?', {'biorel':biorel})

def bioent_biocon_reference_link(bioent_biocon):
    return bioent_biocon.link + '/reference'

#Bioconcept links
def biocon_link(biocon):
    return '/' + lower(biocon.biocon_type) + '/' + biocon.format_name

#Bioentrel links
def bioentrel_link(bioentrel):
    return '/' + lower(bioentrel.biorel_type) + '/' + bioentrel.format_name

#Bioentmultirel links
def bioentmultirel_link(bioentmultirel):
    return '/' + lower(bioentmultirel.biorel_type) + '/' + bioentmultirel.format_name

#Chemical links
def chemical_link(chemical):
    return '/chemical/' + chemical.format_name

#Reference links
def reference_link(reference):
    return '/reference/' + reference.format_name

def reference_evidence_link(reference):
    return reference.link + '/evidence'
def reference_phenotype_link(reference):
    return reference.link + '/phenotype'
def reference_go_link(reference):
    return reference.link + '/go'
def reference_interaction_link(reference):
    return reference.link + '/interaction'

def author_link(author):
    return '/author/' + author.format_name

def experiment_link(experiment):
    return '/experiment/' + experiment.format_name
def strain_link(strain):
    return '/strain/' + strain.format_name
