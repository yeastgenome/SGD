CREATE OR REPLACE TRIGGER ReferenceReftype_BIUR
--
-- Before insert or update trigger for reference_reftype table
--
  BEFORE INSERT OR UPDATE ON reference_reftype
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.reference_reftype_id IS NULL) THEN
        SELECT reference_reftype_seq.NEXTVAL INTO :new.reference_reftype_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.reference_reftype_id != :old.reference_reftype_id) THEN    
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

END ReferenceReftype_BIUR;
/
SHOW ERROR