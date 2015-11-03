from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, Float, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import ToJsonMixin, UpdateWithJsonMixin, Base
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.reference import Reference

__author__ = 'kelley, sweng66'

class Strain(Dbentity):
    __tablename__ = 'straindbentity'

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    strain_type = Column('strain_type', String)
    genotype = Column('genotype', String)
    genbank_id = Column('genbank_id', String)
    assembly_size = Column('assembly_size', Integer)
    fold_coverage = Column('fold_coverage', Float)
    scaffold_number = Column('scaffold_number', Integer)
    longest_scaffold = Column('longest_scaffold', Integer)
    scaffold_nfifty = Column('scaffold_nfifty', Integer)
    feature_count = Column('feature_count', Integer)

    #Relationships
    taxonomy = relationship(Taxonomy, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'STRAIN', 'inherit_condition': id == Dbentity.id}

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'date_created', 
                     'created_by', 'sgdid', 'dbentity_status', 'strain_type', 'genotype', 
                     'genbank_id', 'assembly_size', 'fold_coverage', 'scaffold_number',
                     'longest_scaffold', 'scaffold_nfifty', 'feature_count']
    __eq_fks__ = [('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('urls', 'strain.StrainUrl', True),
                  ('summaries', 'strain.StrainSummary', True)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['strain_type']

    def __init__(self, obj_json, session):
        self.taxonomy_id = obj_json['taxonomy_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json


class StrainUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    strain = relationship(Strain, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('strain', Strain, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.strain is None else self.strain.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.strain_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(strain_id=newly_created_object.strain_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

class StrainSummary(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_summary'

    id = Column('summary_id', Integer, primary_key=True)
    summary_type = Column('summary_type', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    strain = relationship(Strain, uselist=False, backref=backref('summaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'summary_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('strain', Strain, False),
                  ('references', 'strain.StrainSummaryReference', False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.strain is None else self.strain.unique_key()), self.summary_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.strain_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(strain_id=newly_created_object.strain_id)\
            .filter_by(summary_type=newly_created_object.summary_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class StrainSummaryReference(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_summary_reference'

    id = Column('summary_reference_id', Integer, primary_key=True)
    summary_id = Column('summary_id', Integer, ForeignKey(StrainSummary.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    reference_order = Column('reference_order', Integer)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    summary = relationship(StrainSummary, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('strain_summaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'reference_order', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('summary', StrainSummary, False),
                  ('reference', Reference, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, summary, reference_id, reference_order):
        self.reference_order = reference_order
        self.summary = summary
        self.reference_id = reference_id
        self.source = self.summary.source

    def unique_key(self):
        return (None if self.summary is None else self.summary.unique_key()), (None if self.reference is None else self.reference.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        # reference, status = Reference.create_or_find(obj_json, session)
        # if status == 'Created':
        #    raise Exception('Reference not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(summary_id=parent_obj.id)\
            .filter_by(reference_id=obj_json['reference_id'])

        if current_obj is None:
            newly_created_object = cls(parent_obj, obj_json['reference_id'], obj_json['reference_order'])
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'
