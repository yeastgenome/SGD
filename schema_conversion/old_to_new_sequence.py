'''
Created on Mar 22, 2013

@author: kpaskov
'''
from model_old_schema.config import DBUSER as OLD_DBUSER
from schema_conversion import cache, create_or_update
from schema_conversion.old_to_new_bioentity import id_to_bioent
from schema_conversion.output_manager import OutputCreator
import model_old_schema


id_to_bioent_bioent = {}
id_to_sequence = {}
id_to_seqtag = {}


"""
---------------------Create------------------------------
"""

def create_sequence(old_seq):
    from model_new_schema.sequence import Sequence as NewSequence  
    old_feat_location = old_seq.current_feat_location
    feature_id = old_seq.feature_id if old_seq.seq_type == 'genomic' else create_protein_id(old_seq.feature_id)  
      
    if feature_id in id_to_bioent and old_seq.is_current == 'Y':
        if old_feat_location is not None:
            return NewSequence(feature_id, old_seq.seq_version, old_feat_location.coord_version, old_feat_location.min_coord, 
                       old_feat_location.max_coord, old_feat_location.strand, old_seq.is_current, old_seq.seq_length, old_seq.ftp_file, 
                       old_seq.residues, old_seq.seq_type, old_seq.source, old_feat_location.rootseq_id, 'S288C',
                       sequence_id=old_seq.id, 
                       date_created=old_seq.date_created, created_by=old_seq.created_by)
        else:
            return NewSequence(feature_id, old_seq.seq_version, None, None, None, None, old_seq.is_current, old_seq.seq_length, old_seq.ftp_file, 
                       old_seq.residues, old_seq.seq_type, old_seq.source, None, 'S288C',
                       sequence_id=old_seq.id, 
                       date_created=old_seq.date_created, created_by=old_seq.created_by)
    else:
        return None
    
def create_transcript_id(gene_id):
    return gene_id + 50000

def create_protein_id(gene_id):
    return gene_id + 100000
    
def create_transcript(old_seq):
    from model_new_schema.bioentity import Transcript as NewTranscript
    gene_id = old_seq.feature_id
    if old_seq.seq_type == 'genomic' and old_seq.is_current == 'Y' and gene_id in id_to_bioent:
        return NewTranscript(gene_id, 'Active', bioent_id=create_transcript_id(old_seq.feature_id))
    else:
        return None
    
def create_protein(old_seq):
    from model_new_schema.bioentity import Protein as NewProtein
    transcript_id = create_transcript_id(old_seq.feature_id)
    if old_seq.seq_type == 'protein' and old_seq.is_current == 'Y' and transcript_id in id_to_bioent:
        return NewProtein(transcript_id, 'Active', bioent_id=create_protein_id(old_seq.feature_id))
    else:
        return None
    
def create_seqtag(old_seq):
    from model_new_schema.sequence import Seqtag as NewSeqtag
    if old_seq.is_current == 'Y' and old_seq.feature_id in id_to_seqtag:
        old_feat_location = old_seq.current_feat_location
        if old_feat_location is not None:
            return NewSeqtag(None, None, None, None, None, None, None, None, old_feat_location.min_coord, old_seq.seq_length, seqtag_id=old_seq.feature_id)
        else:
            return NewSeqtag(None, None, None, None, None, None, None, None, None, old_seq.seq_length, seqtag_id=old_seq.feature_id)
    else:
        return None
    
def create_seqtag2(child_id, parent_id):
    from model_new_schema.sequence import Seqtag as NewSeqtag
    if child_id in id_to_seqtag and parent_id in id_to_bioent:
        return NewSeqtag(parent_id, None, None, None, None, None, None, None, None, None, seqtag_id=child_id)
    else:
        return None
    
"""
---------------------Convert------------------------------
"""  

def convert_sequence(old_model, session):
    from model_old_schema.sequence import Sequence as OldSequence
    from model_old_schema.feature import FeatRel as OldFeatRel

    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.sequence import Sequence as NewSequence, Seqtag as NewSeqtag
      
    output_creator = OutputCreator()

    #Cache bioents
    key_maker = lambda x: x.id
    cache(NewBioentity, id_to_bioent, key_maker, session, output_creator, 'bioent')

    #Create new transcripts if they don't exist, or update the database if they do.
    old_seqs = old_model.execute(model_old_schema.model.get(OldSequence), OLD_DBUSER)
    values_to_check = ['gene_id']
    create_or_update(old_seqs, id_to_bioent, create_transcript, key_maker, values_to_check, session, output_creator, 'transcript')
    
    #Create new proteins if they don't exist, or update the database if they do.
    values_to_check = ['transcript_id']
    create_or_update(old_seqs, id_to_bioent, create_protein, key_maker, values_to_check, session, output_creator, 'protein')

    #Cache sequences
    key_maker = lambda x: x.id
    cache(NewSequence, id_to_sequence, key_maker, session, output_creator, 'sequence')
    
    #Create new sequences if they don't exist, or update the database if they do.
    values_to_check = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'is_current', 'length', 'ftp_file', 
                       'residues', 'seq_type', 'rootseq_id', 'date_created', 'created_by']
    create_or_update(old_seqs, id_to_sequence, create_sequence, key_maker, values_to_check, session, output_creator, 'sequence')
    
    #Cache seqtags
    key_maker = lambda x: x.id
    cache(NewSeqtag, id_to_seqtag, key_maker, session, output_creator, 'seqtag')
    
    #Update seqtag min_coord and length.
    values_to_check = ['chrom_coord', 'length']
    create_or_update(old_seqs, id_to_seqtag, create_seqtag, key_maker, values_to_check, session, output_creator, 'seqtag')

    #Update seqtag seq_id
    old_feat_rels = old_model.execute(model_old_schema.model.get(OldFeatRel, relationship_type='part of'), OLD_DBUSER)
    
    
    
    