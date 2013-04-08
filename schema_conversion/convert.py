'''
Created on Jan 16, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion.old_to_new_bioentity import convert_feature, \
    convert_protein
from schema_conversion.old_to_new_biorelation import interaction_to_biorel
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import datetime
import model_new_schema
import model_old_schema




def convert():    
    commit=True
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()
        
        #convert_feature(old_session, new_session)
        convert_protein(old_session, new_session)
                
        if commit:
            new_session.commit()
    finally:
        new_session.close()

def prepare_schema_connection(model_cls, config_cls):
    model_cls.SCHEMA = config_cls.SCHEMA
    class Base(object):
        __table_args__ = {'schema': config_cls.SCHEMA, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.metadata = model_cls.Base.metadata
    engine = create_engine("%s://%s:%s@%s/%s" % (config_cls.DBTYPE, config_cls.DBUSER, config_cls.DBPASS, config_cls.DBHOST, config_cls.DBNAME), convert_unicode=True, pool_recycle=3600)
    model_cls.Base.metadata.bind = engine
    session_maker = sessionmaker(bind=engine)
        
    return session_maker
            
def convert_references_to_references(session, old_model):
    print "Convert References to References"
    from model_old_schema.reference import Reference as OldReference

    rs = old_model.execute(model_old_schema.model.get(OldReference), OLD_DBUSER)
    
    count = 0;
    time = datetime.datetime.now()
    for r in rs:
        new_r = reference_to_reference(r)
        model_new_schema.model.add(new_r, session)       
            
        count = count+1
        if count%1000 == 0:
            session.commit()
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(rs)) +  " " + str(new_time - time)
            time = new_time
                        
def convert_interactions_to_biorels(old_model, new_model, min_id, max_id):
    print "Convert Interaction to Biorelations"
    from model_old_schema.interaction import Interaction as OldInteraction
    from model_new_schema.biorelation import Interaction as NewInteraction
    from model_new_schema.evidence import Interevidence
    
    time = datetime.datetime.now()
    inters = old_model.execute(model_old_schema.model.get_filter(OldInteraction, OldInteraction.id>=min_id, OldInteraction.id < max_id), OLD_DBUSER)
    
    count = 0;
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for old_interaction in inters:
        if not new_model.execute(model_new_schema.model.exists(Interevidence, id=old_interaction.id), NEW_DBUSER):
            bait_id = old_interaction.features['Bait'].id
            hit_id = old_interaction.features['Hit'].id
    
            if bait_id < hit_id:
                new_biorel = new_model.execute(model_new_schema.model.get_first(NewInteraction, source_bioent_id=bait_id, sink_bioent_id=hit_id), NEW_DBUSER)
                direction = 'bait-hit'
            else:
                new_biorel = new_model.execute(model_new_schema.model.get_first(NewInteraction, source_bioent_id=hit_id, sink_bioent_id=bait_id), NEW_DBUSER)
                direction = 'hit-bait'
    
            if new_biorel is None:
                new_biorel = interaction_to_biorel(old_interaction)
    
            reference_id = None
            if len(old_interaction.references) > 0:
                reference_id = old_interaction.references[0].id
            observable = None
            if len(old_interaction.observables) > 0:
                observable = old_interaction.observables[0]
            qualifier = None
            if len(old_interaction.qualifiers) > 0:
                qualifier = old_interaction.qualifiers[0]
            note = None
            if len(old_interaction.notes) > 0:
                note = old_interaction.notes[0]
    
            new_biorel.evidences.append(Interevidence(old_interaction.experiment_type, reference_id, 4932, direction, old_interaction.annotation_type,
                                           old_interaction.modification, old_interaction.source, observable, qualifier, note,
                                           old_interaction.interaction_type,
                                           evidence_id=old_interaction.id, date_created=old_interaction.date_created,
                                           created_by=old_interaction.created_by))
    
            new_model.execute(model_new_schema.model.add(new_biorel), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(inters)) +  " " + str(new_time - time)
            time = new_time
        
def update_phenotypes(old_model, min_id, max_id, session):
    print "Convert Phenotypes to Bioconcepts"

    from model_old_schema.phenotype import Phenotype_Feature as OldPhenotype_Feature

    time = datetime.datetime.now()
    ps = old_model.execute(model_old_schema.model.get_filter(OldPhenotype_Feature, OldPhenotype_Feature.id>=min_id, OldPhenotype_Feature.id < max_id), OLD_DBUSER)

    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for p in ps:
        new_p = update_phenoevidence(p)
        if new_p is not None:
            model_new_schema.model.add(new_p, session=session)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(ps)) +  " " + str(new_time - time)
            time = new_time
   
def fill_typeahead_table(old_model, new_model, bioent_type):
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.search import Typeahead

    time = datetime.datetime.now()
    fs = new_model.execute(model_new_schema.model.get(NewBioentity, bioent_type=bioent_type), NEW_DBUSER)
    print len(fs)
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for f in fs:
        name = f.name
        if name is not None:
            for i in range (0, len(name)):
                if not new_model.execute(model_new_schema.model.exists(Typeahead, name=name[:i], full_name=name), NEW_DBUSER):
                    typeahead = Typeahead(name[:i], name, 'BIOENT', f.id)
                    new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)

        secondary_name = f.secondary_name
        if secondary_name is not None and secondary_name != name:
            for i in range (0, len(secondary_name)):
                if not new_model.execute(model_new_schema.model.exists(Typeahead, name=secondary_name[:i], full_name=secondary_name), NEW_DBUSER):
                    typeahead = Typeahead(secondary_name[:i], secondary_name, 'BIOENT', f.id)
                    new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)
        
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(fs)) +  " " + str(new_time - time)
            time = new_time
            
def fill_typeahead_table_aliases(old_model, new_model):
    from model_new_schema.bioentity import Alias as NewAlias
    from model_new_schema.search import Typeahead

    time = datetime.datetime.now()
    aliases = new_model.execute(model_new_schema.model.get(NewAlias, used_for_search='Y'), NEW_DBUSER)

    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for alias in aliases:
        name = alias.name
        if name is not None:
            #for i in range (0, len(name)):
            if not new_model.execute(model_new_schema.model.exists(Typeahead, name=name, full_name=name), NEW_DBUSER):
                typeahead = Typeahead(name, name, 'BIOENT', alias.bioent_id)
                new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)
        
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(aliases)) +  " " + str(new_time - time)
            time = new_time
 
def convert_alias_to_alias(old_model, new_model):
    from model_old_schema.feature import AliasFeature as OldAliasFeature
    from model_new_schema.bioentity import Alias as NewAlias

    time = datetime.datetime.now()
    aliases = old_model.execute(model_old_schema.model.get(OldAliasFeature),OLD_DBUSER)
   
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for alias in aliases:
        new_a = NewAlias(alias.alias_name, alias.alias_type, alias.used_for_search, 
                         alias_id=alias.id, bioent_id=alias.feature_id, date_created = alias.date_created, created_by = alias.created_by)
        new_model.execute(model_new_schema.model.add(new_a), NEW_DBUSER, commit=True)

        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(aliases)) +  " " + str(new_time - time)
            time = new_time 
            
def convert_phenotypes_to_observable(old_model, new_model):
    print "Convert Phenotypes to Bioconcepts"

    from model_old_schema.phenotype import Phenotype_Feature as OldPhenotype_Feature
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon

    time = datetime.datetime.now()
    ps = old_model.execute(model_old_schema.model.get(OldPhenotype_Feature), OLD_DBUSER)
    
    id_new_ps = {}
    new_ps = new_model.execute(model_new_schema.model.get(NewPhenoevidence), NEW_DBUSER)
    for new_p in new_ps:
        id_new_ps[new_p.id] = new_p
        
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for p in ps:
        phenoevidence = id_new_ps[p.id]
        if phenoevidence.qualifier is None:
            qualifier = 'None';
            observable = 'None';
            if p.qualifier is not None:
                qualifier = p.qualifier
            if p.observable is not None:
                observable = p.observable
                
            #Set qualifier for phenoevidence.
            phenoevidence.qualifier = qualifier
                        
            bioent = new_model.execute(model_new_schema.model.get_first(NewBioentity, id=p.feature_id), NEW_DBUSER)

            #Find or create bioconcept
            new_biocon = new_model.execute(model_new_schema.model.get_first(NewPhenotype, observable=observable), NEW_DBUSER)
            if new_biocon is None:
                new_biocon = NewPhenotype(observable, biocon_id=p.id, date_created=p.date_created, created_by=p.created_by)
                new_model.execute(model_new_schema.model.add(new_biocon), NEW_DBUSER, commit=True)
                biocon_id = p.id
            else:
                biocon_id = new_biocon.id
                
            #Find or create BioentBiocon
            bioent_biocon = new_model.execute(model_new_schema.model.get_first(NewBioentBiocon, bioent_id=bioent.id, biocon_id=biocon_id), NEW_DBUSER)
            if bioent_biocon is None:
                bioent_biocon = NewBioentBiocon(bioent, biocon_id)
            bioent_biocon.evidences.append(phenoevidence)
         
            new_model.execute(model_new_schema.model.add(bioent_biocon), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(ps)) +  " " + str(new_time - time)
            time = new_time

          

    
if __name__ == "__main__":
    convert()