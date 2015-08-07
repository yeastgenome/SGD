--/
CREATE OR REPLACE TRIGGER ALLELE_TRIGGER
BEFORE INSERT ON allele
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.allele_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER AUTHOR_RESPONSE_TRIGGER
BEFORE INSERT ON author_response
FOR EACH ROW
BEGIN
SELECT author_response_seq.nextval INTO :new.author_response_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER CONTIG_TRIGGER
BEFORE INSERT ON contig
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.contig_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER CONTIG_URL_TRIGGER
BEFORE INSERT ON contig_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER DNASEQUENCEANNOTATION_TRIGGER
BEFORE INSERT ON dnasequenceannotation
FOR EACH ROW
BEGIN
SELECT annotation_seq.nextval INTO :new.annotation_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER DNASEQUENCE_EXTENSION_TRIGGER
BEFORE INSERT ON dnasequence_extension
FOR EACH ROW
BEGIN
SELECT dnaseqext_seq.nextval INTO :new.dnasequence_extension_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER EXPERIMENT_TRIGGER
BEFORE INSERT ON experiment
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.experiment_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER GENOMERELEASE_TRIGGER
BEFORE INSERT ON genomerelease
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.genomerelease_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER MUTANT_TRIGGER
BEFORE INSERT ON mutant
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.mutant_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER OBSERVABLE_TRIGGER
BEFORE INSERT ON observable
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.observable_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER PHENOTYPE_TRIGGER
BEFORE INSERT ON phenotype
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.phenotype_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER POSTTRANSANNOTATION_TRIGGER
BEFORE INSERT ON posttranslationalannotation
FOR EACH ROW
BEGIN
SELECT annotation_seq.nextval INTO :new.annotation_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER PROTEINDOMAIN_TRIGGER
BEFORE INSERT ON proteindomain
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.proteindomain_id FROM DUAL;
END;
/

--/
CREATE OR REPLACE TRIGGER PROTEINDOMAIN_URL_TRIGGER
BEFORE INSERT ON proteindomain_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/
