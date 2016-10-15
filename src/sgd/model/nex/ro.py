from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'sweng66'

class Ro(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'ro'

    id = Column('ro_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    roid = Column('roid', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'roid']
    __eq_fks__ = [('source', Source, False),
                  ('urls', 'ro.RoUrl', True),
                  ('children', 'ro.RoRelation', True)]
    __id_values__ = ['id', 'format_name', 'roid']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.created_by = 'OTTO'
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return obj_json['roid']


class RoUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'ro_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    ro = relationship(Ro, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.ro is None else self.ro.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.ro_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(ro_id=newly_created_object.ro_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class RoRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'ro_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    parent_id = Column('parent_id', Integer, ForeignKey(Ro.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Ro.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Ro, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Ro, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Ro, False),
                  ('child', Ro, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, relation_type):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.relation_type = relation_type

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Ro.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Child reference not found: ' + str(obj_json))

        relation_type = obj_json["relation_type"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id)\
            .filter_by(relation_type=relation_type).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, relation_type)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self):
        obj_json = self.child.to_min_json()
        obj_json['source'] = self.child.source.to_min_json()
        obj_json['relation_type'] = self.relation_type
