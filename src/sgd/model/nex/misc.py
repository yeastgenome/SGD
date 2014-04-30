from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin


__author__ = 'kpaskov'

class Source(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'source'

    id = Column('source_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    link = None

    __eq_values__ = ['id', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(self.display_name)

    def unique_key(self):
        return self.format_name

eco_id_to_category = {'ECO:0000000': None,
                      'ECO:0000046': 'expression',
                      'ECO:0000048': 'expression',
                      'ECO:0000049': 'expression',
                      'ECO:0000055': 'expression',
                      'ECO:0000066': 'binding',
                      'ECO:0000096': 'binding',
                      'ECO:0000104': 'expression',
                      'ECO:0000106': 'expression',
                      'ECO:0000108': 'expression',
                      'ECO:0000110': 'expression',
                      'ECO:0000112': 'expression',
                      'ECO:0000116': 'expression',
                      'ECO:0000126': 'expression',
                      'ECO:0000136': 'binding',
                      'ECO:0000226': 'binding',
                      'ECO:0000229': 'binding',
                      'ECO:0000230': 'binding',
                      'ECO:0000231': 'expression',
                      'ECO:0000295': 'expression'}

class Experiment(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'experiment'

    id = Column('experiment_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    eco_id = Column('eco_id', String)
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'eco_id', 'category',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(obj_json.get('display_name'))
        if obj_json.get('eco_id') in eco_id_to_category:
            self.category = eco_id_to_category[obj_json.get('eco_id')]

    def unique_key(self):
        return self.format_name

alternative_reference_strains = {'CEN.PK', 'D273-10B', 'FL100', 'JK9-3d', 'RM11-1a', 'SEY6210', 'SK1', 'Sigma1278b', 'W303', 'X2180-1A', 'Y55'}

class Strain(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    is_alternative_reference = Column('is_alternative_reference', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'is_alternative_reference',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(obj_json.get('display_name')).replace('.', '')
        self.is_alternative_reference = 1 if obj_json.get('display_name') in alternative_reference_strains else 0

    def unique_key(self):
        return self.format_name
       
class Url(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'url'
    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', ForeignKey(Source.id))
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type, 'polymorphic_identity': "URL"}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category', 'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.category, self.display_name, self.format_name

class Alias(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type, 'polymorphic_identity': "ALIAS"}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category', 'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.display_name, self.format_name, self.category

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['evidences'] = [x.to_json() for x in self.alias_evidences]
        if self.category in {'PDB identifier', 'UniParc ID', 'UniProt/Swiss-Prot ID', 'UniProt/TrEMBL ID',
            'UniProtKB Subcellular Location', 'Protein version ID', 'EC number', 'InterPro', 'RefSeq protein version ID',
            'RefSeq nucleotide version ID', 'TPA protein version ID', 'DNA version ID', 'NCBI protein GI', 'TPA Accession',
            'PDB ID', 'RefSeq Accession', 'TC number', 'PANTHER'}:
            obj_json['protein'] = True
        else:
            obj_json['protein'] = False
        return obj_json

class Relation(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'relation'

    id = Column('relation_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type, 'polymorphic_identity': "RELATION"}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = ['source', 'parent', 'child']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.format_name, self.class_type, self.relation_type

class Experimentrelation(Relation):
    __tablename__ = 'experimentrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Experiment.id))
    child_id = Column('child_id', Integer, ForeignKey(Experiment.id))

    #Relationships
    parent = relationship(Experiment, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Experiment, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Experimentalias(Alias):
    __tablename__ = 'experimentalias'

    id = Column('alias_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))

    #Relationships
    experiment = relationship(Experiment, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'experiment_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT', 'inherit_condition': id == Alias.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('experiment_id'))
