'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, UniqueMixin, SCHEMA
from model_old_schema.feature import Feature
from model_old_schema.pubmed import get_medline_data, MedlineJournal
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
import datetime
       
class Reference(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'reference'

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
    journal_id = Column('journal_no', Integer, ForeignKey('bud.journal.journal_no'))
    book_id = Column('book_no', Integer, ForeignKey('bud.book.book_no'))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    journal = relationship('Journal', uselist=False, lazy='subquery')
    journal_abbrev = association_proxy('journal', 'abbreviation',
                                    creator=lambda x: Journal.as_unique(Session.object_session(self), abbreviation=x))
    
    book = relationship('Book', uselist=False, lazy='subquery')
    
    abst = relationship("Abstract", cascade='all,delete', uselist=False, lazy='subquery')
    abstract = association_proxy('abst', 'text')
    
    features = relationship(Feature, secondary= Table('ref_curation', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    
    author_references = relationship('AuthorReference', cascade='all,delete',
                             backref=backref('reference'),
                            collection_class=attribute_mapped_collection('order'))
    
    authorNames = association_proxy('author_references', 'author_name')
    authors = association_proxy('author_references', 'author', 
                                creator=lambda k, v: AuthorReference(session=None, author=v, order=k, ar_type='Author'))
    refTypes = relationship("RefType", cascade='all,delete', secondary= Table('ref_reftype', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    refTypeNames = association_proxy('refTypes', 'name')
    
    litGuides = relationship("LitGuide", cascade='all,delete')
    litGuideTopics = association_proxy('litGuides', 'topic')
    
    curations = relationship('RefCuration', cascade='all,delete')

    
    def __init__(self, session, pubmed_id):
        self.pubmed_id = pubmed_id
        self.pdf_status='N'
        self.source='PubMed script'
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
        pubmed = get_medline_data(pubmed_id)
            
        #Set basic information for the reference.
        self.status = pubmed.publish_status
        self.citation = pubmed.citation
        self.year = pubmed.year
        self.pdf_status = pubmed.pdf_status
        self.pages = pubmed.pages
        self.volume = pubmed.volume
        self.title = pubmed.title
        self.issue = pubmed.issue
                        
        pubmed = get_medline_data(self.pubmed_id)

        #Add the journal.
        self.journal = Journal.as_unique(session, abbreviation=pubmed.journal_abbrev)
        
        #Add the abstract.
        if pubmed.abstract_txt is not None and not pubmed.abstract_txt == "": 
            self.abst = Abstract.as_unique(session, reference_id = self.id, text = pubmed.abstract_txt)
                
        #Add the authors.
        order = 0
        for author_name in pubmed.authors:
            order += 1
            self.authors[order] = Author.as_unique(session, name=author_name)
                
        #Add the ref_type
        self.refType = RefType.as_unique(session, name=pubmed.pub_type)
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(Reference.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.title, self.pubmed_id
        return 'Reference(title=%s, pubmed_id=%s)' % data
    
class Book(Base, EqualityByIDMixin):
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
    
class Journal(Base, EqualityByIDMixin, UniqueMixin):
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
    
    def __init__(self, session, abbreviation):
        medlineJournal = MedlineJournal(abbreviation)
        self.abbreviation = abbreviation
        self.full_name = medlineJournal.journal_title
        self.issn = medlineJournal.issn
        self.essn = medlineJournal.essn
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, abbreviation):
        return abbreviation

    @classmethod
    def unique_filter(cls, query, abbreviation):
        return query.filter(Journal.abbreviation == abbreviation)

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data
    
class RefTemp(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_temp'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_temp_no', Integer, primary_key = True)
    pubmed_id = Column('pubmed', Integer)
    citation = Column('citation', String)
    fulltext_url = Column('fulltext_url', String)
    abstract = Column('abstract', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __init__(self, session, pubmed_id):    
        self.pubmed_id = pubmed_id

        pubmed = get_medline_data(pubmed_id)
        self.citation = pubmed.citation
        self.abstract = pubmed.abstract_txt

        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(RefTemp.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.pubmed_id
        return 'RefTemp(pubmed_id=%s)' % data
    
class RefBad(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_bad'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    pubmed_id = Column('pubmed', Integer, primary_key = True)
    dbxref_id = Column('dbxref_id', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __init__(self, session, pubmed_id, dbxref_id=None):
        self.pubmed_id = pubmed_id
        self.dbxref_id = dbxref_id
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(RefBad.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.pubmed_id, self.dbxref_id
        return 'RefBad(pubmed_id=%s, dbxref_id=%s)' % data  
    
class Author(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'author'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('author_no', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, session, name):
        self.name = name
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Author.name == name)

    def __repr__(self):
        data = self.name
        return 'Author(name=%s)' % data   
    
class AuthorReference(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'author_editor'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('author_editor_no', Integer, primary_key = True)
    author_id = Column('author_no', Integer, ForeignKey('bud.author.author_no'))
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    order = Column('author_order', Integer)
    type = Column('author_type', String)
        
    def __init__(self, session, author, order, ar_type):
        self.author = author
        self.order = order
        self.type = ar_type
        
    @classmethod
    def unique_hash(cls, author, order, ar_type):
        return '%s_%s_%s_%s' % (author, order, ar_type)  

    @classmethod
    def unique_filter(cls, query, author, reference_id, order, ar_type):
        return query.filter(AuthorReference.order == order, AuthorReference.author == author, AuthorReference.ar_type == ar_type)
    
    author = relationship('Author') 
    author_name = association_proxy('author', 'name')
    
class Abstract(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'abstract'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'), primary_key = True)
    text = Column('abstract', String)
   
    def __init__(self, session, text, reference_id):
        self.text = text
        self.reference_id = reference_id
        
    @classmethod
    def unique_hash(cls, text, reference_id):
        return reference_id

    @classmethod
    def unique_filter(cls, query, text, reference_id):
        return query.filter(Abstract.reference_id == reference_id)

    def __repr__(self):
        data = self.text
        return 'Abstract(text=%s)' % data  
    
class RefType(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_type'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_type_no', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('ref_type', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, session, name):
        self.name = name;
        self.source = 'NCBI'
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(RefType.name == name)

    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class LitGuide(Base, EqualityByIDMixin, UniqueMixin):
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
    
    def __init__(self, session, reference_id, topic):
        self.reference_id = reference_id
        self.topic = topic
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, reference_id, topic):
        return '%s_%s' % (reference_id, topic)  

    @classmethod
    def unique_filter(cls, query, reference_id, topic):
        return query.filter(LitGuide.reference_id == reference_id, LitGuide.topic == topic)

    def __repr__(self):
        data = self.topic, self.reference_id, self.features
        return 'LitGuide(topic=%s, reference_id=%s, features=%s)' % data  
    
class RefCuration(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_curation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_curation_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    task = Column('curation_task', String)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    comment = Column('curator_comment', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    feature = relationship('Feature', uselist=False)

    def __init__(self, session, reference_id, task, feature_id):
        self.task = task
        self.reference_id = reference_id
        self.feature_id = feature_id
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, reference_id, task, feature_id):
        return '%s_%s_%s' % (reference_id, task, feature_id)  

    @classmethod
    def unique_filter(cls, query, reference_id, task, feature_id):
        return query.filter(RefCuration.reference_id == reference_id, RefCuration.task == task, RefCuration.feature_id == feature_id)

    def __repr__(self):
        if self.feature_id is not None:
            data = self.task, self.feature, self.comment
            return 'RefCuration(task=%s, feature=%s, comment=%s)' % data
        else:
            data = self.task, self.comment
            return 'RefCuration(task=%s, feature=None, comment=%s)' % data 
    
