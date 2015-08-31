CREATE OR REPLACE TRIGGER Allele_AUDR
--
--  After a row in the allele table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON allele
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'FORMAT_NAME', :old.allele_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'DISPLAY_NAME', :old.allele_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'OBJ_URL', :old.allele_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'SOURCE_ID', :old.allele_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'BUD_ID', :old.allele_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('ALLELE', 'DESCRIPTION', :old.allele_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.allele_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('ALLELE', :old.allele_id, v_row, USER);

  END IF;

END Allele_AUDR;
/
SHOW ERROR
