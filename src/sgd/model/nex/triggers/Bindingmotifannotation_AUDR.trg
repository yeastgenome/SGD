CREATE OR REPLACE TRIGGER Bindingmotifannotation_AUDR
--
--  After a Bindingmotifannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON bindingmotifannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF  (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url) 
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'OBJ_URL', :old.annotation_id, :old.obj_url, :new.obj_url, USER);
    END IF;

    IF (:old.motif_id != :new.motif_id)
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'MOTIF_ID', :old.annotation_id, :old.motif_id, :new.motif_id, USER);
    END IF;

    IF (:old.logo_url != :new.logo_url)
    THEN
        AuditLog.InsertUpdateLog('BINDINGMOTIFANNOTATION', 'LOGO_URL', :old.annotation_id, :old.logo_url, :new.logo_url, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' || 
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.obj_url || '[:]' || :old.motif_id || '[:]' ||
             :old.logo_url || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('BINDINGMOTIFANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Bindingmotifannotation_AUDR;
/
SHOW ERROR