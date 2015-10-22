from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.dbentity import Dbentity

__author__ = 'sweng66'

class ReferenceUnlink(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'reference_unlink'

    id = Column('reference_unlink_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                                                                                 
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])

    __eq_values__ = ['id', 'reference_id', 'dbentity_id', 'bud_id', 'created_by', 
                     'date_created']
    __id_values__ = ['id']
    __eq_fks__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

    def to_semi_json(self):
        return self.to_min_json()
