'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.biorelation import Biorelation
from model_new_schema.link_maker import add_link, bioent_link, bioent_wiki_link
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, Numeric, Float
import datetime
# Following two imports are necessary for SQLAlchemy



class Bioentity(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'newbioent'
    
    id = Column('bioent_id', Integer, primary_key=True)
    official_name = Column('name', String)
    bioent_type = Column('bioent_type', String)
    dbxref_id = Column('dbxref', String)
    source = Column('source', String)
    status = Column('status', String)
    secondary_name = Column('secondary_name', String)
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': bioent_type,
                       'polymorphic_identity':"BIOENTITY",
                       'with_polymorphic':'*'}
    
    bioconcepts = association_proxy('bioent_biocon', 'bioconcept')
    aliases = relationship("Alias")
    alias_names = association_proxy('aliases', 'name')
    seq_ids = association_proxy('sequences', 'id')
    type = "BIOENTITY"
            
    def __init__(self, name, bioent_type, dbxref, source, status, secondary_name,
                 session=None, bioent_id=None, date_created=None, created_by=None):
        self.official_name = name
        self.bioent_type = bioent_type
        self.dbxref_id = dbxref
        self.source = source
        self.status = status
        self.secondary_name = secondary_name
        
        if session is None:
            self.id = bioent_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.date_created = datetime.datetime.now()
            self.created_by = session.user
    
    #Database hybrid properties
    @hybrid_property
    def biorelations(self):
        return set(self.biorel_source + self.biorel_sink)
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.alias_names)
    
    #Names and links    
    @hybrid_property
    def name(self):
        return self.official_name if self.secondary_name is None else self.secondary_name      
    @hybrid_property
    def full_name(self, include_link=True):
        return self.secondary_name + ' (' + self.official_name + ')'
    @hybrid_property
    def link(self):
        return bioent_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link) 
    @hybrid_property
    def full_name_with_link(self):
        return add_link(self.full_name, self.link) 
    @hybrid_property
    def wiki_name_with_link(self):
        return add_link(self.wiki_link, self.wiki_link)
    @hybrid_property
    def wiki_link(self):
        return bioent_wiki_link(self)
     
    @classmethod
    def unique_hash(cls, bioent_type, name):
        return '%s_%s' % (bioent_type, name) 

    @classmethod
    def unique_filter(cls, query, bioent_type, name):
        return query.filter(Bioentity.bioent_type == bioent_type, Bioentity.name == name)
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name, self.bioent_type
        return '%s(id=%s, name=%s, bioent_type=%s)' % data       

class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.newbioent.bioent_id'))
    name = Column('name', String)
    alias_type = Column('alias_type', String)
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
        
    def __init__(self, name, alias_type, used_for_search, session=None, alias_id=None, bioent_id=None, date_created=None, created_by=None):
        self.name = name
        self.alias_type = alias_type
        self.used_for_search = used_for_search
        
        if session is None:
            self.id = alias_id
            self.bioent_id = bioent_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.date_created = datetime.datetime.now()
            self.created_by = session.user             
                       
class Gene(Bioentity):
    __tablename__ = "gene"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    qualifier = Column('qualifier', String)
    attribute = Column('attribute', String)
    name_description = Column('short_description', String)
    headline = Column('headline', String)
    description = Column('description', String)
    genetic_position = Column('genetic_position', String)
    gene_type = Column('gene_type', String)
    
    transcript_ids = association_proxy('transcripts', 'id')
    
    __mapper_args__ = {'polymorphic_identity': 'GENE',
                       'inherit_condition': id == Bioentity.id}

    def __init__(self, name, gene_type, taxon_id, dbxref, source, secondary_name,
                 qualifier, attribute, short_description, headline, description, genetic_position,
                 session=None, bioent_id=None, date_created=None, created_by=None):
        Bioentity.__init__(self, name, 'GENE', taxon_id, dbxref, source, secondary_name, 
                            session=session, bioent_id=bioent_id, date_created=date_created, created_by=created_by)
        self.qualifier = qualifier
        self.attribute = attribute
        self.short_description = short_description
        self.headline = headline
        self.description = description
        self.genetic_position = genetic_position
        self.gene_type = gene_type
        
class Transcript(Bioentity):
    __tablename__ = "transcript"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    gene_id = Column('gene_id', Integer, ForeignKey(Gene.id))
    
    __mapper_args__ = {'polymorphic_identity': "TRANSCRIPT",
                       'inherit_condition': id == Bioentity.id}
    
    gene = relationship('Gene', uselist=False, backref='transcripts', primaryjoin="Transcript.gene_id==Gene.id")
    protein_ids = association_proxy('proteins', 'id')

    def __init__(self, gene_id, status, bioent_id=None):
        Bioentity.__init__(self, 'Transcript', 'TRANSCRIPT', None, 'SGD', status, None, bioent_id=bioent_id)
        self.gene_id = gene_id
        
class Protein(Bioentity):
    __tablename__ = "protein"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    transcript_id = Column('transcript_id', Integer, ForeignKey(Transcript.id))
    
    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Float)
    cai = Column('cai', Float)
    length = Column('length', Integer)
    n_term_seq = ('n_term_seq', String)
    c_term_seq = ('c_term_seq', String)
    codon_bias = ('codon_bias', Float)
    fop_score = Column('fop_score', Float)
    gravy_score = Column('gravy_score', Float)
    aromaticity_score = Column('aromaticity_score', Float)
    
    ala = Column('ala', Integer)
    arg = Column('arg', Integer)
    asn = Column('asn', Integer)
    asp = Column('asp', Integer)
    cys = Column('cys', Integer)
    gln = Column('gln', Integer)
    glu = Column('glu', Integer)
    gly = Column('gly', Integer)
    his = Column('his', Integer)
    ile = Column('ile', Integer)
    leu = Column('leu', Integer)
    lys = Column('lys', Integer)
    met = Column('met', Integer)
    phe = Column('phe', Integer)
    pro = Column('pro', Integer)
    thr = Column('thr', Integer)
    ser = Column('ser', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)
    
    aliphatic_index = Column('aliphatic_index', Float)
    atomic_comp_H = Column('atomic_comp_h', Integer)
    atomic_comp_S = Column('atomic_comp_s', Integer)
    atomic_comp_N = Column('atomic_comp_n', Integer)
    atomic_comp_O = Column('atomic_comp_o', Integer)
    atomic_comp_C = Column('atomic_comp_c', Integer)
    half_life_yeast_in_vivo = Column('half_life_yeast_in_vivo', String)
    half_life_ecoli_in_vivo = Column('half_life_ecoli_in_vivo', String)
    half_life_mammalian_reticulocytes_in_vitro = Column('half_life_mammalian', String)
    extinction_coeff_no_cys_residues_as_half_cystines = Column('extinction_coeff_no_half', Integer)
    extinction_coeff_all_cys_residues_reduced = Column('extinction_coeff_all_reduced', Integer)
    extinction_coeff_all_cys_residues_as_half_cystines = Column('extinction_coeff_all_half', Integer)
    extinction_coeff_all_cys_pairs_form_cystines = Column('extinction_coeff_all_pairs', Integer)
    instability_index = Column('instability_index', Float)
    molecules_per_cell = Column('molecules_per_cell', Integer)
     
    transcript = relationship('Transcript', uselist=False, backref='proteins', primaryjoin="Protein.transcript_id==Transcript.id")
    
    __mapper_args__ = {'polymorphic_identity': "PROTEIN",
                       'inherit_condition': id == Bioentity.id}
    
    def get_percent_aa(self, aa_abrev):
        return "{0:.2f}".format(100*float(getattr(self, aa_abrev))/self.length) + '%'

    def __init__(self, name, secondary_name, transcript_id, 
                 molecular_weight, pi, cai, length, n_term_seq, c_term_seq,
                 codon_bias, fop_score, gravy_score, aromaticity_score, 
                 ala, arg, asn, asp, cys, gln, glu, gly, his, ile, leu, lys, met, phe, pro, thr, ser, trp, tyr, val, 
                 aliphatic_index, atomic_comp_H, atomic_comp_S, atomic_comp_N, atomic_comp_O, atomic_comp_C,
                 half_life_yeast_in_vivo, half_life_ecoli_in_vivo, half_life_mammalian_reticulocytes_in_vitro,
                 extinction_coeff_no_cys_residues_as_half_cystines, extinction_coeff_all_cys_residues_reduced,
                 extinction_coeff_all_cys_residues_appear_as_half_cystines, extinction_coeff_all_cys_pairs_form_cystines,
                 instability_index, molecules_per_cell,
                 bioent_id=None, date_created=None, created_by=None):
        Bioentity.__init__(self, name, 'PROTEIN', None, 'SGD', None, secondary_name, bioent_id=bioent_id, date_created=date_created, created_by=created_by)
        self.transcript_id = transcript_id
        
        self.molecular_weight = molecular_weight
        self.pi = pi
        self.cai = cai
        self.length = length
        self.n_term_seq = n_term_seq
        self.c_term_seq = c_term_seq
        self.codon_bias = codon_bias
        self.fop_score = fop_score
        self.gravy_score = gravy_score
        self.aromaticity_score = aromaticity_score
        
        self.ala = ala
        self.arg = arg
        self.asn = asn
        self.asp = asp
        self.cys = cys
        self.gln = gln
        self.glu = glu
        self.gly = gly
        self.his = his
        self.ile = ile
        self.leu = leu
        self.lys = lys
        self.met = met
        self.phe = phe
        self.pro = pro
        self.thr = thr
        self.ser = ser
        self.trp = trp
        self.tyr = tyr
        self.val = val
        
        self.aliphatic_index = aliphatic_index
        self.atomic_comp_H = atomic_comp_H
        self.atomic_comp_S = atomic_comp_S
        self.atomic_comp_N = atomic_comp_N
        self.atomic_comp_O = atomic_comp_O
        self.atomic_comp_C = atomic_comp_C
        self.half_life_yeast_in_vivo = half_life_yeast_in_vivo
        self.half_life_ecoli_in_vivo = half_life_ecoli_in_vivo
        self.half_life_mammalian_reticulocytes_in_vitro = half_life_mammalian_reticulocytes_in_vitro
        self.extinction_coeff_all_cys_pairs_form_cystines = extinction_coeff_all_cys_pairs_form_cystines
        self.extinction_coeff_all_cys_residues_as_half_cystines  = extinction_coeff_all_cys_residues_appear_as_half_cystines
        self.extinction_coeff_all_cys_residues_reduced = extinction_coeff_all_cys_residues_reduced
        self.extinction_coeff_no_cys_residues_as_half_cystines = extinction_coeff_no_cys_residues_as_half_cystines
        self.instability_index = instability_index
        self.molecules_per_cell = molecules_per_cell
        

        
        