from src.sgd.convert import basic_convert, remove_nones
from src.sgd.convert.util import read_obo
from sqlalchemy.sql.expression import or_

__author__ = 'sweng66'

key_switch = {'id': 'chebiid', 'name': 'display_name', 'def': 'description'}

def chebi_starter(bud_session_maker):
    
    from src.sgd.model.bud.phenotype import ExperimentProperty

    bud_session = bud_session_maker()

    chebi_to_date_created = {}
        
    parent_to_children = dict()
    source = 'EBI'
    is_obsolete_id = dict()
    # downloaded from ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo
    terms = read_obo('CHEBI',
                     'src/sgd/convert/data/chebi.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)

    loaded = []
    
    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY

    from src.sgd.model.nex.chebi import Chebi

    nex_session = get_nex_session()
    chebiid_to_id = dict([(x.chebiid, x.id) for x in nex_session.query(Chebi).all()])
    nex_session.close()

    for term in terms:

        name = term['display_name']
        loaded.append(name.lower())

        chebiid = term['chebiid']
        if chebiid in is_obsolete_id:
            continue
        if not chebiid.startswith("CHEBI:"):
            continue
        if len(name) > 500:
            continue

        if chebiid in chebiid_to_id:
            continue

        print chebiid
        if chebiid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[chebiid]:
                child_id = child['chebiid']
                child['created_by'] = dbuser
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        term['created_by'] = dbuser
        term['created_by'] = dbuser
        aliases = []
        for alias in term['aliases']:
            alias['created_by'] = dbuser
            aliases.append(alias)
        term['aliases'] = aliases
        term['urls'].append({'display_name': 'ChEBI',
                              'link': 'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=' + term['chebiid'],
                              'source': {'display_name': source},
                              'url_type': 'ChEBI',
                              'created_by': dbuser})
        yield term

    for bud_obj in bud_session.query(ExperimentProperty).filter(ExperimentProperty.type=='Chemical_pending'):
        name = bud_obj.value.lower()
        if name in loaded:
            continue
        yield {'display_name': bud_obj.value,
               'bud_id': bud_obj.id,
               'chebiid': "NTR:" + str(bud_obj.id),
               'source': {'display_name': 'SGD'},
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by}

    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, chebi_starter, 'chebi', lambda x: x['display_name'])


