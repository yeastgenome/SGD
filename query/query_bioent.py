'''
Created on Jul 9, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Locus, Bioentity
from query import session
from sqlalchemy.orm.util import with_polymorphic

bioent_type_to_class = {'LOCUS':Locus}

#Used for LSP (Locus summary page) and go_evidence, phenotype_evidence, interaction_evidence pages. 
#Also used for interaction_overview, interaction_evidence table
#Also used for go_graph, interaction_graph.
def get_bioent(bioent_name, bioent_type, print_query=False):
    '''
    get_bioent('YFL039C', print_query=True)

    SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by, sprout.gene.bioent_id AS sprout_gene_bioent_id, sprout.gene.short_description AS sprout_gene_short_description, sprout.gene.qualifier AS sprout_gene_qualifier, sprout.gene.attribute AS sprout_gene_attribute, sprout.gene.headline AS sprout_gene_headline, sprout.gene.description AS sprout_gene_description, sprout.gene.genetic_position AS sprout_gene_genetic_position, sprout.gene.gene_type AS sprout_gene_gene_type 
    FROM sprout.bioent LEFT OUTER JOIN sprout.gene ON sprout.gene.bioent_id = sprout.bioent.bioent_id 
    WHERE sprout.bioent.name = :name_1
    '''
    query = session.query(with_polymorphic(Bioentity, [bioent_type_to_class[bioent_type]])).filter(Bioentity.format_name==bioent_name)
    bioent = query.first()
    if print_query:
        print query
    return bioent

#Used to create go_overview, phenotype_overview, go_evidence, and phenotype_evidence tables
def get_bioent_id(bioent_name, bioent_type, print_query=False):
    '''
    get_bioent_id('YFL039C', print_query=True)

    SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by 
    FROM sprout.bioent 
    WHERE sprout.bioent.name = :name_1
    '''
    query = session.query(Bioentity).filter(Bioentity.bioent_type==bioent_type).filter(Bioentity.format_name==bioent_name)
    bioent = query.first()
    bioent_id = None
    if bioent is not None:
        bioent_id = bioent.id
    if print_query:
        print query
    return bioent_id