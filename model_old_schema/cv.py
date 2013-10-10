'''
Created on Apr 22, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.general import Dbxref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class CVTerm(Base, EqualityByIDMixin):
    __tablename__ = 'cv_term'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cv_term_no', Integer, primary_key = True)
    cv_no = Column('cv_no', Integer)
    name = Column('term_name', String)
    dbxref_id = Column('dbxref_id', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    definition = Column('cvterm_definition', String)
    
    parents = association_proxy('parent_rels', 'parent')
    synonyms = association_proxy('cv_synonyms', 'synonym')
    dbxrefs = association_proxy('cv_dbxrefs', 'dbxref')
        
class CVTermRel(Base, EqualityByIDMixin):
    __tablename__ = 'cvterm_relationship'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cvterm_relationship_no', Integer, primary_key = True)
    child_id = Column('child_cv_term_no', Integer, ForeignKey(CVTerm.id))
    parent_id = Column('parent_cv_term_no', Integer, ForeignKey(CVTerm.id))
    relationship_type = Column('relationship_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    child = relationship(CVTerm, uselist=False, primaryjoin="CVTermRel.child_id==CVTerm.id", backref='parent_rels')
    parent = relationship(CVTerm, uselist=False, primaryjoin="CVTermRel.parent_id==CVTerm.id")
    
class CVTermSynonym(Base, EqualityByIDMixin):
    __tablename__ = 'cvterm_synonym'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cvterm_synonym_no', Integer, primary_key = True)
    cvterm_id = Column('cv_term_no', Integer, ForeignKey(CVTerm.id))
    synonym = Column('term_synonym', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    cvterm = relationship(CVTerm, uselist=False, backref='cv_synonyms')
    
class CVTermDbxref(Base, EqualityByIDMixin):
    __tablename__ = 'cvterm_dbxref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cvterm_dbxref_no', Integer, primary_key = True)
    cvterm_id = Column('cv_term_no', Integer, ForeignKey(CVTerm.id))
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    
    cvterm = relationship(CVTerm, uselist=False, backref='cv_dbxrefs')
    dbxref = relationship(Dbxref, uselist=False)
                        