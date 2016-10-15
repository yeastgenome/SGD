from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.ro import Ro

__author__ = 'sweng66'

class Disease(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'disease'

    id = Column('disease_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    doid = Column('doid', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'doid']
    __eq_fks__ = [('source', Source, False),
                  ('urls', 'disease.DiseaseUrl', True),
                  ('aliases', 'disease.DiseaseAlias', True),
                  ('children', 'disease.DiseaseRelation', True)]
    __id_values__ = ['id', 'format_name', 'doid']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return obj_json['doid']


class DiseaseUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'disease_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    disease_id = Column('disease_id', Integer, ForeignKey(Disease.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    disease = relationship(Disease, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.disease is None else self.disease.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.disease_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(disease_id=newly_created_object.disease_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class DiseaseAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'disease_alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    disease_id = Column('disease_id', Integer, ForeignKey(Disease.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    disease = relationship(Disease, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.disease is None else self.disease.unique_key()), self.display_name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.disease_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(disease_id=newly_created_object.disease_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class DiseaseRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'disease_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    parent_id = Column('parent_id', Integer, ForeignKey(Disease.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Disease.id, ondelete='CASCADE'))
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Disease, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Disease, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)
    ro = relationship(Ro, uselist=False)

    __eq_values__ = ['id', 'ro_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('ro', Ro, False),
                  ('parent', Disease, False),
                  ('child', Disease, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, ro_id):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.ro_id = ro_id

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Disease.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Child reference not found: ' + str(obj_json))

        ro_id = obj_json["ro_id"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, ro_id)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self):
        obj_json = self.child.to_min_json()
        obj_json['source'] = self.child.source.to_min_json()
        obj_json['ro'] = self.child.ro.to_min_json()