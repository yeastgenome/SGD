Create OR REPLACE TRIGGER ArchLocuschange_BIUDR
--
-- Before insert, update or deleted trigger for arch_locuschange table
--
  BEFORE INSERT OR UPDATE OR DELETE ON arch_locuschange
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.username%TYPE;
  v_CanDelete       NUMBER;
BEGIN
  IF INSERTING THEN

    IF (:new.archive_id IS NULL) THEN
        SELECT archive_seq.NEXTVAL INTO :new.archive_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.changed_by);

  ELSIF UPDATING THEN

    IF (:new.archive_id != :old.archive_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.locus_id != :old.locus_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.source_id != :old.source_id) THEN
	RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.bud_id != :old.bud_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.change_type != :old.change_type) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.old_value != :old.old_value) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.new_value != :old.new_value) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.date_changed != :old.date_changed) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.changed_by != :old.changed_by) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.date_archived != :old.date_archived) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  ELSE

    v_CanDelete := CheckDelete.CheckTableDelete('ARCH_LOCUSCHANGE');  

  END IF;

END ArchLocuschange_BIUDR;
/
SHOW ERROR
