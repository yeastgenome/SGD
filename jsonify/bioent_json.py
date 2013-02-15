'''
Created on Feb 12, 2013

@author: kpaskov
'''
def bioent_mini(bioent):
    return {'name':bioent.secondary_name, 'official_name':bioent.name, 'description':bioent.description, 'bioent_type':bioent.bioent_type, 
            'full_name':bioent.secondary_name + '(' + bioent.name + ')'}

def bioent_small(bioent):
    aliases = ', '.join(bioent.alias_names)
    return {'name':bioent.secondary_name, 'official_name':bioent.name, 'aliases':aliases, 'description':bioent.description,
            'source':bioent.source, 'status':bioent.status, 'qualifier':bioent.qualifier, 'attribute':bioent.attribute,
            'name_description':bioent.short_description, 'bioent_type':bioent.bioent_type}

def bioent_large(bioent):
    basic_info = bioent_small(bioent)
    
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    phenotypes = [bioent_biocon_small(bioent_biocon) for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'PHENOTYPE']
        
    return {'basic_info':basic_info, 'genetic_position':bioent.genetic_position, 'interaction_count':len(interactions), 'interactions':interactions,
            'phenotype_count':len(phenotypes), 'phenotypes':phenotypes}

def biorel_small(biorel):
    source_bioent = bioent_mini(biorel.source_bioent)
    sink_bioent = bioent_mini(biorel.sink_bioent)
    return {'name': source_bioent['name'] + '---' + sink_bioent['name'],'official_name':biorel.name, 'source':source_bioent, 'sink':sink_bioent, 'evidence_count':biorel.evidence_count} 
    
def biorel_large(biorel):
    basic_info = biorel_small(biorel)
            
    references = set([evidence.reference for evidence in biorel.evidences])
    json_references = [reference_mini(reference) for reference in references]
    json_evidences = [interevidence_small(evidence) for evidence in biorel.evidences]
    
    return {'basic_info':basic_info, 'evidences':json_evidences, 'references': json_references}

def evidence_small(evidence):
    if evidence.reference is not None:
        reference = reference_mini(evidence.reference)
    else:
        reference = None
    return {'experiment_type':evidence.experiment_type, 'reference':reference}
    
def interevidence_small(evidence):
    basic_info = evidence_small(evidence)

    basic_info['annotation_type'] = evidence.annotation_type
    basic_info['modification'] = evidence.modification
    basic_info['direction'] = evidence.modification
    basic_info['interaction_type'] = evidence.interaction_type
    basic_info['observable'] = evidence.observable
    basic_info['qualifier'] = evidence.qualifier
    return basic_info

def phenoevidence_small(evidence): 
    basic_info = evidence_small(evidence)
    
    basic_info['mutant'] = evidence.mutant_type
    basic_info['source'] = evidence.source
    basic_info['comment'] = evidence.experiment_comment
    return basic_info

def reference_mini(ref):
    return {'source': ref.source, 'status':ref.status, 'pdf_status':ref.pdf_status, 'citation': ref.citation, 'year': str(ref.year),
            'pubmed_id': str(ref.pubmed_id), 'date_published': ref.date_published, 'date_revised':ref.date_revised, 'issue':ref.issue,
            'page':ref.page, 'volume':ref.volume, 'title':ref.title, 'doi':ref.doi} 

def reference_small(ref):
    basic_info = reference_mini(ref)

    if ref.book_id is not None:
        basic_info['book'] = ref.book.title
    else:
        basic_info['book'] = None
    if ref.journal_id is not None:
        basic_info['journal'] = ref.journal.full_name
    else:
        basic_info['journal'] = None
    basic_info['abstract'] = ref.abstract
    return basic_info
    
def reference_large(ref):
    basic_info = reference_small(ref)

    return {'basic_info':basic_info} 

def bioent_biocon_small(bioent_biocon):
    return {'biocon_type':bioent_biocon.bioconcept.biocon_type, 'biocon_name':bioent_biocon.bioconcept.name, 'evidence_count':bioent_biocon.evidence_count,
            'name':bioent_biocon.name}    
    
def bioent_biocon_large(bioent_biocon):
    basic_info = bioent_biocon_small(bioent_biocon)
    bioent = bioent_mini(bioent_biocon.bioentity)
    biocon = biocon_small(bioent_biocon.bioconcept)
    
    references = set([evidence.reference for evidence in bioent_biocon.evidences if evidence.reference is not None])
    json_references = [reference_mini(reference) for reference in references]
    json_evidences = [phenoevidence_small(evidence) for evidence in bioent_biocon.evidences]
    return {'basic_info':basic_info, 'bioent':bioent, 'biocon':biocon, 'evidences':json_evidences, 'references':json_references} 

def biocon_small(biocon):
    return {'biocon_type':biocon.biocon_type, 'name':biocon.name}    
    
def biocon_large(biocon):
    basic_info = biocon_small(biocon)
    return {'basic_info':basic_info} 
    
    