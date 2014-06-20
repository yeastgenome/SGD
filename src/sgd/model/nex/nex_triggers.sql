/* Alias */
DROP TRIGGER ALIAS_TRIGGER;
--/
CREATE TRIGGER ALIAS_TRIGGER
BEFORE INSERT ON alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

/* URL */
DROP TRIGGER URL_TRIGGER;
--/
CREATE TRIGGER URL_TRIGGER
BEFORE INSERT ON url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/


/* Relation */
DROP TRIGGER RELATION_TRIGGER;
--/
CREATE TRIGGER RELATION_TRIGGER
BEFORE INSERT ON relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

/* Paragraph */
DROP TRIGGER PARA_TRIGGER;
--/
CREATE TRIGGER PARA_TRIGGER
BEFORE INSERT ON paragraph
FOR EACH ROW
BEGIN
SELECT para_seq.nextval INTO :new.paragraph_id FROM DUAL;
END;
/

DROP TRIGGER PARAREF_TRIGGER;
--/
CREATE TRIGGER PARAREF_TRIGGER
BEFORE INSERT ON paragraph_reference
FOR EACH ROW
BEGIN
SELECT pararef_seq.nextval INTO :new.paragraph_reference_id FROM DUAL;
END;
/

/* Evelements */
DROP TRIGGER SOURCE_TRIGGER;
--/
CREATE TRIGGER SOURCE_TRIGGER
BEFORE INSERT ON source
FOR EACH ROW
BEGIN
SELECT source_seq.nextval INTO :new.source_id FROM DUAL;
END;
/

DROP TRIGGER STRAIN_TRIGGER;
--/
CREATE TRIGGER STRAIN_TRIGGER
BEFORE INSERT ON strain
FOR EACH ROW
BEGIN
SELECT strain_seq.nextval INTO :new.strain_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENT_TRIGGER;
--/
CREATE TRIGGER EXPERIMENT_TRIGGER
BEFORE INSERT ON experiment
FOR EACH ROW
BEGIN
SELECT experiment_seq.nextval INTO :new.experiment_id FROM DUAL;
END;
/

/* Evidence */
DROP TRIGGER EVIDENCE_TRIGGER;
--/
CREATE TRIGGER EVIDENCE_TRIGGER
BEFORE INSERT ON evidence
FOR EACH ROW
BEGIN
SELECT evidence_seq.nextval INTO :new.evidence_id FROM DUAL;
END;
/


/* Condition */
DROP TRIGGER CONDITION_TRIGGER;
--/
CREATE TRIGGER CONDITION_TRIGGER
BEFORE INSERT ON condition
FOR EACH ROW
BEGIN
SELECT cond_seq.nextval INTO :new.condition_id FROM DUAL;
END;
/


/* Bioitem */
DROP TRIGGER BIOITEM_TRIGGER;
--/
CREATE TRIGGER BIOITEM_TRIGGER
BEFORE INSERT ON bioitem
FOR EACH ROW
BEGIN
SELECT bioitem_seq.nextval INTO :new.bioitem_id FROM DUAL;
END;
/


/* Bioconcept */
DROP TRIGGER BIOCONCEPT_TRIGGER;
--/
CREATE TRIGGER BIOCONCEPT_TRIGGER
BEFORE INSERT ON bioconcept
FOR EACH ROW
BEGIN
SELECT bioconcept_seq.nextval INTO :new.bioconcept_id FROM DUAL;
END;
/

/* BIOENTITY */
DROP TRIGGER BIOENTITY_TRIGGER;
--/
CREATE TRIGGER BIOENTITY_TRIGGER
BEFORE INSERT ON bioentity
FOR EACH ROW
BEGIN
IF (:new.bioentity_id IS NULL) THEN
SELECT bioentity_seq.nextval INTO :new.bioentity_id FROM DUAL;
END IF;
END;
/


/* Auxilliary */
DROP TRIGGER AUX_INTERACTION_TRIGGER;
--/
CREATE TRIGGER AUX_INTERACTION_TRIGGER
BEFORE INSERT ON aux_interaction
FOR EACH ROW
BEGIN
SELECT aux_interaction_seq.nextval INTO :new.aux_interaction_id FROM DUAL;
END;
/

DROP TRIGGER DISAMBIG_TRIGGER;
--/
CREATE TRIGGER DISAMBIG_TRIGGER
BEFORE INSERT ON aux_disambig
FOR EACH ROW
BEGIN
SELECT aux_disambig_seq.nextval INTO :new.aux_disambig_id FROM DUAL;
END;
/

/* Chemical */

DROP TRIGGER CHEM_TRIGGER;
--/
CREATE TRIGGER CHEM_TRIGGER
BEFORE INSERT ON chemical
FOR EACH ROW
BEGIN
SELECT chem_seq.nextval INTO :new.chemical_id FROM DUAL;
END;
/

/* Sequence */
DROP TRIGGER DNASEQTAG_TRIGGER;
--/
CREATE TRIGGER DNASEQTAG_TRIGGER
BEFORE INSERT ON dnasequencetag
FOR EACH ROW
BEGIN
SELECT dnaseqtag_seq.nextval INTO :new.dnasequencetag_id FROM DUAL;
END;
/

/* Expression */
DROP TRIGGER EXPDATA_TRIGGER;
--/
CREATE TRIGGER EXPDATA_TRIGGER
BEFORE INSERT ON expressiondata
FOR EACH ROW
BEGIN
SELECT expdata_seq.nextval INTO :new.expressiondata_id FROM DUAL;
END;
/

DROP TRIGGER JOURNAL_TRIGGER;
--/
CREATE TRIGGER JOURNAL_TRIGGER
BEFORE INSERT ON journal
FOR EACH ROW
BEGIN
SELECT journal_seq.nextval INTO :new.journal_id FROM DUAL;
END;
/

DROP TRIGGER BOOK_TRIGGER;
--/
CREATE TRIGGER BOOK_TRIGGER
BEFORE INSERT ON book
FOR EACH ROW
BEGIN
SELECT book_seq.nextval INTO :new.book_id FROM DUAL;
END;
/

DROP TRIGGER AUTHOR_TRIGGER;
--/
CREATE TRIGGER AUTHOR_TRIGGER
BEFORE INSERT ON author
FOR EACH ROW
BEGIN
SELECT author_seq.nextval INTO :new.author_id FROM DUAL;
END;
/


