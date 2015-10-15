CREATE OR REPLACE TRIGGER Proteindomainannotation_AUDR
--
--  After a Proteindomainannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteindomainannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF

    IF  (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.proteindomain_id != :new.proteindomain_id) 
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'PROTEINDOMAIN_ID', :old.annotation_id, :old.proteindomain_id, :new.proteindomain_id, USER);
    END IF;

    IF (:old.start_index != :new.start_index)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'START_INDEX', :old.annotation_id, :old.start_index, :new.start_index, USER);
    END IF;

    IF (:old.end_index != :new.end_index)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'END_INDEX', :old.annotation_id, :old.end_index, :new.end_index, USER);
    END IF;

    IF (:old.date_of_run != :new.date_of_run)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAINANNOTATION', 'DATE_OF_RUN', :old.annotation_id, :old.date_of_run, :new.date_of_run, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.proteindomain_id || '[:]' || :old.start_index || '[:]' ||
             :old.end_index || '[:]' || :old.date_of_run || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINDOMAINANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Proteindomainannotation_AUDR;
/
SHOW ERROR