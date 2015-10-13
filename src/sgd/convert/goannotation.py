from src.sgd.convert import basic_convert
from src.sgd.convert.gpad_config import curator_id, computational_created_by,  \
    go_db_code_mapping, go_ref_mapping, current_go_qualifier, email_receiver, \
    email_subject

__author__ = 'sweng66'

# TAXON_ID = 'NCBITaxon:559292'
TAXON_ID = 4932

qualifier_mapping = { "P": "involved in", "F": "enables", "C": "part of" }

def goannotation_starter(bud_session_maker):

    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.go import Go
    from src.sgd.model.nex.eco import EcoAlias

    from src.sgd.model.bud.go import GoRef
    from src.sgd.model.bud.go import Go as Go_bud
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return

    goid_to_go_id = dict([(x.goid, x.id) for x in nex_session.query(Go).all()])
    evidence_to_eco_id = dict([(x.display_name, x.eco_id) for x in nex_session.query(EcoAlias).all()])

    bud_id_to_reference_id = {}
    pmid_to_reference_id = {}
    sgdid_to_reference_id = {}
    for x in nex_session.query(Reference).all():
        bud_id_to_reference_id[x.bud_id] = x.id
        pmid_to_reference_id[x.pmid] = x.id
        sgdid_to_reference_id[x.sgdid] = x.id
                                                
    sgdid_to_locus_id = {}
    bud_id_to_locus_id = {}
    for x in nex_session.query(Locus).all():
        sgdid_to_locus_id[x.sgdid] = x.id
        bud_id_to_locus_id[x.bud_id] = x.id

    go_no_to_goid = {}
    goid_to_qualifier = {}
    for x in bud_session.query(Go_bud).all():
        goid = str(x.go_go_id)
        while len(goid) < 7:
            goid = '0' + goid
        goid = "GO:" + goid
        go_no_to_goid[x.id] = goid
        goid_to_qualifier[goid] = qualifier_mapping[x.go_aspect]
        
    ## load the annotations with source = 'SGD' and the annotations with go_evidence = 'IEA' from GPAD file

    # get date_assigned from gpi file

    f = open('src/sgd/convert/data/gp_information.559292_sgd')

    uniprot_to_date_assigned = {}
    uniprot_to_sgdid_list = {}
    for line  in f:

        if line.startswith('!'):
            continue

        field = line.strip().split('\t')
        
        if len(field) < 10:
            continue

        # same uniprot ID for multiple RNA entries
        uniprotID = field[1]
        sgdid = field[8].replace('SGD:', '')
        sgdid_list = [] if uniprot_to_sgdid_list.get(uniprotID) is None else uniprot_to_sgdid_list.get(uniprotID)
        sgdid_list.append(sgdid)
        uniprot_to_sgdid_list[uniprotID] = sgdid_list

        for pair in field[9].split('|'):
            if not pair.startswith('go_annotation_complete'):
                continue
            property = pair.split('=')
            date = property[1]
            uniprot_to_date_assigned[uniprotID] = str(date[0:4]) + '-' + str(date[4:6]) + '-' + str(date[6:])
    
    f.close()

    # read through gpad file

    f = open('src/sgd/convert/data/gp_association.559292_sgd')

    read_line = {}
    bad_ref = []

    for line in f:

        if line.startswith('!'):
            continue

        field = line.strip().split('\t')
        if field[9] != 'SGD' and not field[11].startswith('go_evidence=IEA'):
            continue
              
        ## get rid of duplicate lines...
        if line in read_line:
            continue
        read_line[line] = 1

        # db = field[0]                                                                                                      
                                                                                                                           
        ## uniprot ID & SGDIDs
        uniprotID = field[1]
        sgdid_list = uniprot_to_sgdid_list.get(uniprotID)
        if sgdid_list is None:
            print "The UniProt ID = ", uniprotID, " is not mapped to any SGDID."
            continue

        ## go_qualifier
        go_qualifier = field[2]
        if go_qualifier == 'part_of':
            go_qualifier = 'part of'
        if go_qualifier == 'involved_in':
            go_qualifier = 'involved in'
        if 'NOT' in go_qualifier:
            go_qualifier = 'NOT'
        
        ## go_id
        goid = field[3]
        go_id = goid_to_go_id.get(goid)
        if go_id is None:
            print "The GOID = ", goid, " is not in GO table."
            continue

        ## eco_id
        # go_evidence=IMP|id=2113463881|curator_name=Kimberly Van Auken
        annot_prop_dict = annot_prop_to_dict(field[11])
        go_evidence = annot_prop_dict.get('go_evidence')
        eco_id = evidence_to_eco_id.get(go_evidence)
        if eco_id is None:
            print "The go_evidence = ", annotation.go_evidence, " is not in the ECO table."
            continue

        ## source 
        source = field[9]
        
        ## created_by         
        if source != 'SGD' and go_evidence == 'IEA':
            created_by = computational_created_by
        else:
            created_by = curator_id.get(annot_prop_dict.get('curator_name'))


        ## reference_id
        reference_id = None
        if field[4].startswith('PMID:'):
            pmid = field[4][5:]    # PMID:1234567; need to be 1234567                              
            reference_id = pmid_to_reference_id.get(int(pmid))
        else:
            ref_sgdid = go_ref_mapping.get(field[4])
            if ref_sgdid is None:
                if field[4] not in bad_ref:
                    bad_ref.append(field[4])
                print "UNKNOWN REF: ", field[4], ", line=", line
                continue
            reference_id = sgdid_to_reference_id.get(ref_sgdid)
        if reference_id is None:
            print "The PMID = " + str(pmid) + " is not in the REFERENCEDBENTITY table."
            continue

        # assigned_group = field[9]                                                                   
        # eg, SGD for manual cuartion;                                                                   
        # Interpro, UniPathway, UniProtKB, GOC, RefGenome for computational annotation                                               # taxon_id = field[7]                                                                                     

        date_created = str(field[8][0:4]) + '-' + str(field[8][4:6]) + '-' + str(field[8][6:])
        if source == 'SGD':
            date_assigned = uniprot_to_date_assigned.get(uniprotID)
            annotation_type = 'manually curated'
        else:
            date_assigned = date_created
            annotation_type = 'computational'

        for sgdid in sgdid_list:
            locus_id = sgdid_to_locus_id.get(sgdid)
            if locus_id is None:
                print "The sgdid = ", sgdid, " is not in LOCUSDBENTITY table."
                continue
            yield { 'source': {'display_name': source},
                    'locus_id': locus_id,
                    'reference_id': reference_id,
                    'taxonomy_id': taxonomy_id,
                    'go_id': go_id,
                    'eco_id': eco_id,
                    'annotation_type': annotation_type,
                    'go_qualifier': go_qualifier,
                    'date_assigned': date_assigned,
                    'date_created': date_created,
                    'created_by': created_by }

    f.close()

    ## only load the annotations with annotation_type = 'manually curated' and source != 'SGD'
    ## and the annotations with annotation_type = 'high-throughput' and source = 'SGD'
    ## into NEX2 from BUD
    
    for bud_obj in bud_session.query(GoRef).all():

        annotation = bud_obj.go_annotation

        if annotation.source == 'SGD' and annotation.annotation_type == 'manually curated':
            continue
    
        if annotation.annotation_type == 'computational' and annotation.go_evidence == 'IEA':
            continue

        locus_id = bud_id_to_locus_id.get(annotation.feature_id)
        if locus_id is None:
            print "The feature_no = ", annotation.feature_id, " is not in LOCUSDBENTITY table."
            continue

        eco_id = evidence_to_eco_id.get(annotation.go_evidence)
        if eco_id is None:
            print "The go_evidence = ", annotation.go_evidence, " is not in the ECO table."
            continue

        goid = go_no_to_goid[annotation.go_id]
        go_id = goid_to_go_id.get(goid)
        if go_id is None:
            print "The GOID = ", goid, " is not in GO table."
            continue

        reference_id = bud_id_to_reference_id.get(bud_obj.reference_id)
        if reference_id is None:
            print "The reference_no = ", bud_obj.reference_id, " is not in REFERENCEDBENTITY table."
            continue

        qualifier = bud_obj.qualifier
        if qualifier is None:
            qualifier = goid_to_qualifier[goid]

        yield { 'source': {'display_name': annotation.source},
                'locus_id': locus_id,
                'reference_id': reference_id,
                'taxonomy_id': taxonomy_id,
                'go_id': go_id,
                'eco_id': eco_id,
                'annotation_type': annotation.annotation_type,
                'go_qualifier': qualifier,
                'bud_id': bud_obj.id,
                'date_assigned': str(annotation.date_last_reviewed),
                'date_created': str(bud_obj.date_created),
                'created_by': bud_obj.created_by }

    bud_session.close()

def annot_prop_to_dict(annot_prop):

    annot_prop_dict = {}
    for annot_prop in annot_prop.split('|'):
        annot = annot_prop.split('=')
        annot_prop_dict[annot[0]] = annot[1]
    return annot_prop_dict


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, goannotation_starter, 'goannotation', lambda x: (x['locus_id'], x['annotation_type'], x['reference_id'], x['go_id'], x['eco_id']))

