__author__ = 'kpaskov'

'''
This file contains all auxilliary classes. These classes do not contain primary data. Instead, they contain quantites
and aggregations of primary data. These classes are used purely to improve performance.
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Numeric

from bioconcept import Bioconcept
from bioentity import Bioentity
from bioitem import Bioitem
from reference import Reference
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin


class Interaction(Base, EqualityByIDMixin, UpdateByJsonMixin):
    '''
    An interaction is a relationship between a bioentity and another type of object. Interactions aggregate evidence.
    So for example, there may be several pieces of evidence indicating that Bioentity A is associated with Go Term B.
    In that case, we would have a single interaction stating that Bioentity A is associated with Go Term B, and this
    interaction would be used to more quickly generate network diagrams or go enrichment results.
    '''
    __tablename__ = "aux_interaction"
    
    id = Column('aux_interaction_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    interaction_type = Column('interaction_type', String)
    evidence_count = Column('evidence_count', Integer)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('interactions', passive_deletes=True))

    __mapper_args__ = {'polymorphic_on': class_type, 'polymorphic_identity':"INTERACTION"}
    __eq_values__ = ['id', 'format_name', 'class_type', 'interaction_type', 'evidence_count']
    __eq_fks__ = ['bioentity', 'interactor']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('interactor').id)

    def unique_key(self):
        return self.bioentity_id, self.class_type, self.interaction_type, self.format_name
    
class Bioentityinteraction(Interaction, EqualityByIDMixin):
    '''
    A bioentity interaction is an interaction between two bioentities. For example, there may be multiple pieces
    of physical interaction evidence indicating that Bioentity A physically interacts with Bioentity B. In that case
    we would have a single bioentity interaction between Bioentity A and Bioentity B with interaction_type 'Physical
    Interaction'.
    '''
    __tablename__ = "aux_bioentityinteraction"

    id = Column('aux_interaction_id', Integer, primary_key=True)
    interactor_id = Column('interactor_id', Integer, ForeignKey(Bioentity.id))
    direction = Column('direction', String)

    #Relationships
    interactor = relationship(Bioentity, uselist=False, backref=backref('interactions2', passive_deletes=True))

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('interactor').id)
        if self.direction is not None:
            self.format_name = self.format_name + '_' + self.direction


    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id==Interaction.id}
    __eq_values__ = ['id', 'format_name', 'class_type', 'interaction_type', 'evidence_count', 'direction']

class Bioconceptinteraction(Interaction, EqualityByIDMixin):
    '''
    A bioconcept interaction is an interaction between a bioentity and a bioconcept. For example, there may be several
    pieces of evidence indicating that Bioentity A is associated with Go Term B.
    In that case, we would have a single interaction stating that Bioentity A is associated with Go Term B, and this
    interaction would be used to more quickly generate network diagrams or go enrichment results.
    '''
    __tablename__ = "aux_bioconceptinteraction"

    id = Column('aux_interaction_id', Integer, primary_key=True)
    interactor_id = Column('interactor_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    interactor = relationship(Bioconcept, uselist=False, backref=backref('interactions', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT', 'inherit_condition': id==Interaction.id}

class Bioiteminteraction(Interaction, EqualityByIDMixin):
    '''
    A bioitem interaction is an interaction between a bioentity and a bioitem. For example, there may be several pieces
    of evidence indicating that Bioentity A is associated with Protein Domain B. In that case, we would have a single
    interaction stating that Bioentity A is associated with Protein Domain B, and that interaction would be used
    to more quickly generate network diagrams.
    '''
    __tablename__ = "aux_bioiteminteraction"

    id = Column('aux_interaction_id', Integer, primary_key=True)
    interactor_id = Column('interactor_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    interactor = relationship(Bioitem, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id==Interaction.id}

class Referenceinteraction(Interaction, EqualityByIDMixin):
    '''
    A reference interaction is an interaction between a bioentity and a reference. For example, there may be several
    pieces of evidence associating Bioentity A with Reference B. In that case, we would have a single interaction
    stating that Bioentity A is associated with Reference B, and that interaction would be used to more quickly generate
    network diagrams.
    '''
    __tablename__ = "aux_referenceinteraction"

    id = Column('aux_interaction_id', Integer, primary_key=True)
    interactor_id = Column('interactor_id', Integer, ForeignKey(Reference.id))

    #Relationships
    interactor = relationship(Reference, uselist=False, backref=backref('reference_interactions', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id==Interaction.id}
    
class Disambig(Base, EqualityByIDMixin, UpdateByJsonMixin):
    '''
    The disambig class is used to disambiguate urls. Given a disambig_key (the identifier in a url) and a class_type
    or subclass_type, we query the disambig table for the object's identifier. For example, the disambig_key might be
    'ACT1', and the class_type might be 'BIOENTITY' and subclass_type 'LOCUS'. In this case, the identifier would be
    the id for the ACT1 locus in the locusbioentity table.
    '''
    __tablename__ = 'aux_disambig'
    
    id = Column('aux_disambig_id', Integer, primary_key=True)
    disambig_key = Column('disambig_key', String)
    class_type = Column('class', String)
    subclass_type = Column('subclass', String)
    identifier = Column('obj_id', String)

    __eq_values__ = ['id', 'disambig_key', 'class_type', 'subclass_type', 'identifier']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.disambig_key = obj_json.get('disambig_key').replace('/', '-').replace(' ', '_')
        
    def unique_key(self):
        return self.disambig_key, self.class_type, self.subclass_type

    def to_json(self):
        json_obj = UpdateByJsonMixin.to_json(self)
        json_obj['disambig_key'] = json_obj['disambig_key'].lower()
        return json_obj
    
class Locustabs(Base, EqualityByIDMixin, UpdateByJsonMixin):
    '''
    The locus tabs class indicates which tabs should be showing for a given locus.
    '''
    __tablename__ = 'aux_locustabs'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    summary_tab = Column('summary', Integer)
    sequence_tab = Column('seq', Integer)
    history_tab = Column('history', Integer)
    literature_tab = Column('literature', Integer)
    go_tab = Column('go', Integer)
    phenotype_tab = Column('phenotype', Integer)
    interaction_tab = Column('interactions', Integer)
    expression_tab = Column('expression', Integer)
    regulation_tab = Column('regulation', Integer)
    protein_tab = Column('protein', Integer)
    wiki_tab = Column('wiki', Integer)
    sequence_section = Column('seq_section', Integer)

    __eq_values__ = ['id', 'summary_tab', 'history_tab', 'literature_tab', 'go_tab', 'phenotype_tab', 'interaction_tab',
                     'expression_tab', 'regulation_tab', 'protein_tab', 'sequence_tab', 'wiki_tab', 'sequence_section']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.id

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        new_obj_json = {'id': obj_json['id']}
        for key, value in obj_json.iteritems():
            if key != 'id':
                new_obj_json[key] = value == 1
        return new_obj_json