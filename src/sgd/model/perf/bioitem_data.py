from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Bioitem
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class BioitemDetails(Base):
    __tablename__ = 'bioitem_details'

    id = Column('bioitem_details_id', Integer, primary_key=True)
    obj_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioitem_id, class_type, json):
        self.obj_id = bioitem_id
        self.class_type = class_type
        self.json = json

class BioitemEnrichment(Base):
    __tablename__ = 'bioitem_enrichment'

    id = Column('bioitem_enrichment_id', Integer, primary_key=True)
    obj_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioitem_id, class_type, json):
        self.obj_id = bioitem_id
        self.class_type = class_type
        self.json = json