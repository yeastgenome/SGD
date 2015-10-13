CREATE OR REPLACE TRIGGER Phenotypeannotation_BIUR
--
-- Before insert or update trigger for the phenotypeannotation table
--
  BEFORE INSERT OR UPDATE ON phenotypeannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
  v_DoesPhenotypeExist  apo.apo_id%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.annotation_id IS NULL) THEN
        SELECT annotation_seq.NEXTVAL INTO :new.annotation_id FROM DUAL;
    END IF; 

    v_DoesPhenotypeExist := CheckPhenotype(:new.experiment_id, 'experiment_type');
    v_DoesPhenotypeExist := CheckPhenotype(:new.mutant_id, 'mutant_type');

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.annotation_id != :old.annotation_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    v_DoesPhenotypeExist := CheckPhenotype(:new.experiment_id, 'experiment_type');
    v_DoesPhenotypeExist := CheckPhenotype(:new.mutant_id, 'mutant_type');

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  END IF;

END Phenotypeannotation_BIUR;
/
SHOW ERROR