__author__ = 'kpaskov'

from sgdbackend_query.query_reference import get_abstract, get_bibentry, get_authors
from sgdbackend_utils import link_gene_names, id_to_reference
from sgdbackend_query.query_auxiliary import get_bioentity_references

'''
-------------------------------Overview---------------------------------------
'''

def make_overview(reference_id):
    reference = dict(id_to_reference[reference_id])
    reference['abstract'] = link_gene_names(get_abstract(reference_id))
    reference['bibentry'] = get_bibentry(reference_id)
    reference['authors'] = get_authors(reference_id)
    bioentity_references = get_bioentity_references(reference_id=reference_id)
    reference['counts'] = {'interaction': len([x for x in bioentity_references if x.class_type == 'INTERACTION']),
                             'go': len([x for x in bioentity_references if x.class_type == 'GO']),
                             'phenotype': len([x for x in bioentity_references if x.class_type == 'PHENOTYPE']),
                             'regulation': len([x for x in bioentity_references if x.class_type == 'REGULATION']),}
    return reference
