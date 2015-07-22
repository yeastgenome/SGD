CREATE OR REPLACE TRIGGER EvidenceUrl_AUDR
--
--  After a row in the evidence_url table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON evidence_url
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'DISPLAY_NAME', :old.url_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'OBJ_URL', :old.url_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'SOURCE_ID', :old.url_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'BUD_ID', :old.url_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.evidence_id != :new.evidence_id)
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'EVIDENCE_ID', :old.url_id, :old.evidence_id, :new.evidence_id, USER);
    END IF;

    IF (:old.url_type != :new.url_type)
    THEN
        AuditLog.InsertUpdateLog('EVIDENCE_URL', 'URL_TYPE', :old.url_id, :old.url_type, :new.url_type, USER);
    END IF;

  ELSE

    v_row := :old.url_id || '[:]' || 
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.evidence_id || '[:]' || :old.url_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('EVIDENCE_URL', :old.url_id, v_row, USER);

  END IF;

END EvidenceUrl_AUDR;
/
SHOW ERROR