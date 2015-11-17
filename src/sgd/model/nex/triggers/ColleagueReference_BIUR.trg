CREATE OR REPLACE TRIGGER ColleagueReference_BIUR
--
-- Before insert or update trigger for colleague_reference table
--
  BEFORE INSERT OR UPDATE ON colleague_reference
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.colleague_reference_id IS NULL) THEN
        SELECT colleague_reference_seq.NEXTVAL INTO :new.colleague_reference_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.colleague_reference_id != :old.colleague_reference_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  END IF;

END ColleagueReference_BIUR;
/
SHOW ERROR