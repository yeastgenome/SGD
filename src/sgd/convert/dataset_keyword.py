from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dataset_keyword_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.keyword import Keyword

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Dataset).all()])
    keyword_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Keyword).all()])

    files = ['src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip().replace('"', '')
            if line:
                pieces = line.split("\t")
                display_name = pieces[1]
                dataset_id = dataset_to_id.get(display_name)
                if dataset_id is None:
                    print "The dataset: ", display_name, " is not in DATASET table."
                    continue
                if len(pieces) <= 17 or pieces[17] == '':
                    continue
                keywords = pieces[17].split("|")
                for keyword in keywords:
                    if keyword == 'translation regulation':
                        keyword = 'translational regulation'
                    keyword_id = keyword_to_id.get(keyword)
                    if keyword_id is None:
                        print "The keyword: ", keyword, " is not in the KEYWORD table."
                        continue
                    yield { "source": { "display_name": 'SGD' },
                            "keyword_id": keyword_id,
                            "dataset_id": dataset_id }

        f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dataset_keyword_starter, 'dataset_keyword', lambda x: (x['keyword_id'], x['dataset_id']))


