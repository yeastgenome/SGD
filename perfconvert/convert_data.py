'''
Created on Oct 29, 2013

@author: kpaskov
'''
from mpmath import ceil
from perfconvert_utils.output_manager import OutputCreator
import logging
import sys

"""
--------------------- Convert Data ---------------------
"""

def create_data(cls, obj_id, json_obj):
    if json_obj is not None:
        return cls(obj_id, json_obj)
    else:
        return None

def update_data(json_obj, old_obj):
    changed = False
    if old_obj.json != json_obj:
        old_obj.json = json_obj
        changed = True
    return changed

def convert_data(session_maker, cls, new_obj_f, label, obj_ids, chunk_size):
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        num_chunks = ceil(1.0*len(obj_ids)/chunk_size)
        for i in range(0, num_chunks):
            chunk_obj_ids = obj_ids[i*chunk_size: (i+1)*chunk_size]
            
            #Grab old objects and current_objs
            old_objs = session.query(cls).filter(cls.id.in_(chunk_obj_ids)).all()
            new_id_to_json_obj = dict([(x, new_obj_f(x)) for x in chunk_obj_ids])
                
            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            
            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_json_obj.keys())
            
            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                json_obj = new_id_to_json_obj[insert_id]
                new_obj = create_data(cls, insert_id, json_obj)
                if new_obj is not None:
                    session.add(new_obj)
                    output_creator.added()
               
            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                json_obj = new_id_to_json_obj[update_id]
                if update_data(json_obj, old_id_to_obj[update_id]):
                    output_creator.changed(update_id, 'json')
                
            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')