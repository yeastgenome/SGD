from src.sgd.convert.into_curate import basic_convert
from sqlalchemy.sql.expression import or_
from interaction_config import genetic_type_to_phenotype, old_phenotype_to_new_phenotype
import sys
# from interaction_config import email_receiver, email_subject
# from util import sendmail

__author__ = 'sweng66'


def geninteractionannotation_starter(bud_session_maker):

    header = True
 
    # biogrid_file = sys.argv[1]
    biogrid_file = "SGD.tab.txt"

    f = open(biogrid_file)     

    for line in f:
        row = line.strip().split('\t')
        
        if genetic_type_to_phenotype.get(row[4]) == None:
            # it is physical interaction
            continue

        if len(row) == 12: 
            if header:
                header = False
            else:
                oldPheno = genetic_type_to_phenotype.get(row[4])          
                newPheno = old_phenotype_to_new_phenotype.get(oldPhone)
                
                mutant_type = ""
                observable = ""
                qualifier = ""
                exptType = ""

                if newPheno != "Not available":
                    mutant_type = "" if newPheno.get('mutant_type') == None else newPheno.get('mutant_type')
                    observable = "" if newPheno.get('observable') == None else newPheno.get('observable')  
                    qualifier = "" if newPheno.get('qualifier') == None else newPheno.get('qualifier')
                    exptType = "" if newPheno.get('experiment_type') == None else newPheno.get('experiment_type')
                
                obj_json = {
                    'dbentity1': {'systematic_name': row[0], 'name': row[0]},
                    'dbentity2': {'systematic_name': row[1], 'name': row[1]},
                    'source': {'name': 'BioGRID'},
                    'taxonomy': {'name': 'Saccharomyces cerevisiae S288c'},
                    'reference': {'pubmed_id': int(row[6])},
                    'mutant_type': mutant_type,
                    'annotation_type': row[9]
                }
                
                if row[10] != '-':
                    obj_json['note'] = row[10]
            
                if exptType:
                    obj_json['experiment'] = { 'name': exptType }
                       
                if observable:
                    obj_json['phenotype'] = {'observable': { 'name': observable }, 
                                             'qualifier':  { 'name': qualifier  }  }
                yield obj_json
                

    f.close()

    sendmail(email_subject, message, email_receiver)


def convert(bud_db, nex_db):
    # no need to pass bud_db for this script
    basic_convert(bud_db, nex_db, geninteractionannotation_starter, 'geninteractionannotation', lambda x: (x['dbentity1']['systematic_name'], None if 'reference' not in x else x['reference']['pubmed_id'], x['mutant_type'], x['annotation_type']))


if __name__ == '__main__':
    # no need to pass pastry...
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

