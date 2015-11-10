Create OR REPLACE TRIGGER Dnasequenceannotation_BIUR
--
-- Before insert or update trigger for dnasequenceannotation table
--
  BEFORE INSERT OR UPDATE ON dnasequenceannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dnasequenceannotation_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.dnasequenceannotation_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.dnasequenceannotation_id != :old.dnasequenceannotation_id) THEN    
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

END Dnasequenceannotation_BIUR;
/
SHOW ERROR
