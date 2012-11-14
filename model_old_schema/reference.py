'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from lit_review.parse import MedlineJournal
from model_old_schema import Base
from model_old_schema.admin import RefCuration
from model_old_schema.config import SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
import datetime
import model_old_schema
       
class Reference(Base):
    __tablename__ = 'reference'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('reference_no', Integer, primary_key = True)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    dbxref_id = Column('dbxref_id', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', String)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_no', String, ForeignKey('bud.journal.journal_no'))
    book_id = Column('book_no', String, ForeignKey('bud.book.book_no'))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    journal = relationship('Journal', uselist=False, lazy='subquery')
    book = relationship('Book', uselist=False, lazy='subquery')
    
    abs = relationship("Abstract", cascade='all,delete', uselist=False, lazy='subquery')
    abstract = association_proxy('abs', 'text',
                                 creator=lambda text: Abstract(text=text, reference_id = id))
    
    features = relationship(Feature, secondary= Table('ref_curation', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    
    author_references = relationship('AuthorReference', cascade='all,delete',
                             backref=backref('reference'),
                            collection_class=attribute_mapped_collection('order'))
    
    authorNames = association_proxy('author_references', 'author_name',
                                    creator=lambda k, v: AuthorReference(order=k, author_name=v, type='Author'))
    authors = association_proxy('author_references', 'author',
                                    creator=lambda k, v: AuthorReference(order=k, author=v, type='Author'))
    
    refTypes = relationship("RefType", cascade='all,delete', secondary= Table('ref_reftype', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    refTypeNames = association_proxy('refTypes', 'name')
    
    litGuides = relationship("LitGuide", cascade='all,delete')
    litGuideTopics = association_proxy('litGuides', 'topic',
                                    creator=lambda topic: LitGuide(topic=topic, reference_id = id))
    
    curations = relationship(RefCuration, viewonly=True)

    
    def __init__(self, pubmed_id):
        self.pubmed_id = pubmed_id
        self.pdf_status='N'
        self.source='PubMed script'
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.title, self.pubmed_id
        return 'Reference(title=%s, pubmed_id=%s)' % data
    
class Book(Base):
    __tablename__ = 'book'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('book_no', Integer, primary_key = True)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', Integer)

    def __repr__(self):
        data = self.title, self.total_pages, self.publisher
        return 'Book(title=%s, total_pages=%s, publisher=%s)' % data
    
class Journal(Base):
    __tablename__ = 'journal'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('journal_no', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', String)
    publisher = Column('publisher', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, abbreviation):
        medlineJournal = MedlineJournal(abbreviation)
        self.abbreviation = abbreviation
        self.full_name = medlineJournal.journal_title
        self.issn = medlineJournal.issn
        self.essn = medlineJournal.essn
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data
    
class RefTemp(Base):
    __tablename__ = 'ref_temp'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_temp_no', Integer, primary_key = True)
    pubmed_id = Column('pubmed', Integer)
    citation = Column('citation', String)
    fulltext_url = Column('fulltext_url', String)
    abstract = Column('abstract', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __init__(self, pubmed_id, citation, fulltext_url, abstract):
        self.pubmed_id = pubmed_id
        self.citation = citation
        self.fulltext_url = fulltext_url
        self.abstract = abstract
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.pubmed_id
        return 'RefTemp(pubmed_id=%s)' % data
    
class RefBad(Base):
    __tablename__ = 'ref_bad'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    pubmed_id = Column('pubmed', Integer, primary_key = True)
    dbxref_id = Column('dbxref_id', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __init__(self, pubmed_id, dbxref_id=None):
        self.pubmed_id = pubmed_id
        self.dbxref_id = dbxref_id
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.pubmed_id, self.dbxref_id
        return 'RefBad(pubmed_id=%s, dbxref_id=%s)' % data  
    
class Author(Base):
    __tablename__ = 'author'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('author_no', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, name):
        self.name = name
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.name
        return 'Author(name=%s)' % data   
    
class AuthorReference(Base):
    __tablename__ = 'author_editor'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('author_editor_no', Integer, primary_key = True)
    author_id = Column('author_no', Integer, ForeignKey('bud.author.author_no'))
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    order = Column('author_order', Integer)
    type = Column('author_type', String)
    
    
    author = relationship('Author') 
    author_name = association_proxy('author', 'name')
    
class Abstract(Base):
    __tablename__ = 'abstract'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'), primary_key = True)
    text = Column('abstract', String)
   
    def __init__(self, text, reference_id):
        self.text = text
        self.reference_id = reference_id

    def __repr__(self):
        data = self.text
        return 'Abstract(text=%s)' % data  
    
class RefType(Base):
    __tablename__ = 'ref_type'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_type_no', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('ref_type', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, name):
        self.name = name;
        self.source = 'NCBI'
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class LitGuide(Base):
    __tablename__ = 'lit_guide'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey("bud.reference.reference_no"))
    topic = Column('literature_topic', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    features = relationship("Feature", secondary= Table('litguide_feat', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True), lazy = 'subquery')
    feature_ids = association_proxy('features', 'id')
    
    def __init__(self, topic, reference_id):
        self.topic = topic
        self.reference_id = reference_id
        self.created_by = model_old_schema.current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.topic, self.reference_id, self.features
        return 'LitGuide(topic=%s, reference_id=%s, features=%s)' % data   
    
