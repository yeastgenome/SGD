
DROP TRIGGER CHEMICAL_ALIAS_TRIGGER;
--/
CREATE TRIGGER CHEMICAL_ALIAS_TRIGGER
BEFORE INSERT ON chemical_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER CHEMICAL_REL_TRIGGER;
--/
CREATE TRIGGER CHEMICAL_REL_TRIGGER
BEFORE INSERT ON chemical_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER CHEMICAL_URL_TRIGGER;
--/
CREATE TRIGGER CHEMICAL_URL_TRIGGER
BEFORE INSERT ON chemical_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_TRIGGER
BEFORE INSERT ON colleague
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.colleague_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_DOC_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_DOC_TRIGGER
BEFORE INSERT ON colleague_document
FOR EACH ROW
BEGIN
SELECT document_seq.nextval INTO :new.document_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_KEYWORD_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_KEYWORD_TRIGGER
BEFORE INSERT ON colleague_keyword
FOR EACH ROW
BEGIN
SELECT colleague_keyword_seq.nextval INTO :new.colleague_keyword_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_LOCUS_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_LOCUS_TRIGGER
BEFORE INSERT ON colleague_locus
FOR EACH ROW
BEGIN
SELECT colleague_locus_seq.nextval INTO :new.colleague_locus_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_RELATION_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_RELATION_TRIGGER
BEFORE INSERT ON colleague_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER COLLEAGUE_URL_TRIGGER;
--/
CREATE TRIGGER COLLEAGUE_URL_TRIGGER
BEFORE INSERT ON colleague_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER CONTIG_TRIGGER;
--/
CREATE TRIGGER CONTIG_TRIGGER
BEFORE INSERT ON contig
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.contig_id FROM DUAL;
END;
/

DROP TRIGGER CONTIG_URL_TRIGGER;
--/
CREATE TRIGGER CONTIG_URL_TRIGGER
BEFORE INSERT ON contig_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER DBENTITY_TRIGGER;
--/
CREATE TRIGGER DBENTITY_TRIGGER
BEFORE INSERT ON dbentity
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.dbentity_id FROM DUAL;
END;
/

DROP TRIGGER DNASEQUENCEANNOTATION_TRIGGER;
--/
CREATE TRIGGER DNASEQUENCEANNOTATION_TRIGGER
BEFORE INSERT ON dnasequenceannotation
FOR EACH ROW
BEGIN
SELECT annotation_seq.nextval INTO :new.annotation_id FROM DUAL;
END;
/

DROP TRIGGER DNASEQUENCE_EXTENSION_TRIGGER;
--/
CREATE TRIGGER DNASEQUENCE_EXTENSION_TRIGGER
BEFORE INSERT ON dnasequence_extension
FOR EACH ROW
BEGIN
SELECT dnaseqext_seq.nextval INTO :new.dnasequence_extension_id FROM DUAL;
END;
/

DROP TRIGGER ENZYME_TRIGGER;
--/
CREATE TRIGGER ENZYME_TRIGGER
BEFORE INSERT ON enzyme
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.enzyme_id FROM DUAL;
END;
/

DROP TRIGGER ENZYME_URL_TRIGGER;
--/
CREATE TRIGGER ENZYME_URL_TRIGGER
BEFORE INSERT ON enzyme_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/


DROP TRIGGER EVIDENCE_TRIGGER;
--/
CREATE TRIGGER EVIDENCE_TRIGGER
BEFORE INSERT ON evidence
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.evidence_id FROM DUAL;
END;
/

DROP TRIGGER EVIDENCE_ALIAS_TRIGGER;
--/
CREATE TRIGGER EVIDENCE_ALIAS_TRIGGER
BEFORE INSERT ON evidence_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER EVIDENCE_RELATION_TRIGGER;
--/
CREATE TRIGGER EVIDENCE_RELATION_TRIGGER
BEFORE INSERT ON evidence_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER EVIDENCE_URL_TRIGGER;
--/
CREATE TRIGGER EVIDENCE_URL_TRIGGER
BEFORE INSERT ON evidence_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENT_TRIGGER;
--/
CREATE TRIGGER EXPERIMENT_TRIGGER
BEFORE INSERT ON experiment
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.experiment_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENT_ALIAS_TRIGGER;
--/
CREATE TRIGGER EXPERIMENT_ALIAS_TRIGGER
BEFORE INSERT ON experiment_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENT_REL_TRIGGER;
--/
CREATE TRIGGER EXPERIMENT_REL_TRIGGER
BEFORE INSERT ON experiment_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENTFACTOR_TRIGGER;
--/
CREATE TRIGGER EXPERIMENTFACTOR_TRIGGER
BEFORE INSERT ON experimentfactor
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.experimentfactor_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENTFACTOR_ALIAS_TRIGGER;
--/
CREATE TRIGGER EXPERIMENTFACTOR_ALIAS_TRIGGER
BEFORE INSERT ON experimentfactor_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENTFACTOR_REL_TRIGGER;
--/
CREATE TRIGGER EXPERIMENTFACTOR_REL_TRIGGER
BEFORE INSERT ON experimentfactor_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER EXPERIMENTFACTOR_URL_TRIGGER;
--/
CREATE TRIGGER EXPERIMENTFACTOR_URL_TRIGGER
BEFORE INSERT ON experimentfactor_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER GENOMERELEASE_TRIGGER;
--/
CREATE TRIGGER GENOMERELEASE_TRIGGER
BEFORE INSERT ON genomerelease
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.genomerelease_id FROM DUAL;
END;
/

DROP TRIGGER GOTERM_TRIGGER;
--/
CREATE TRIGGER GOTERM_TRIGGER
BEFORE INSERT ON goterm
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.goterm_id FROM DUAL;
END;
/

DROP TRIGGER GOTERM_ALIAS_TRIGGER;
--/
CREATE TRIGGER GOTERM_ALIAS_TRIGGER
BEFORE INSERT ON goterm_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER GOTERM_REL_TRIGGER;
--/
CREATE TRIGGER GOTERM_REL_TRIGGER
BEFORE INSERT ON goterm_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER GOTERM_URL_TRIGGER;
--/
CREATE TRIGGER GOTERM_URL_TRIGGER
BEFORE INSERT ON goterm_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER KEYWORD_TRIGGER;
--/
CREATE TRIGGER KEYWORD_TRIGGER
BEFORE INSERT ON keyword
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.keyword_id FROM DUAL;
END;
/

DROP TRIGGER LOCUS_ALIAS_TRIGGER;
--/
CREATE TRIGGER LOCUS_ALIAS_TRIGGER
BEFORE INSERT ON locus_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER LOCUS_DOC_TRIGGER;
--/
CREATE TRIGGER LOCUS_DOC_TRIGGER
BEFORE INSERT ON locus_document
FOR EACH ROW
BEGIN
SELECT document_seq.nextval INTO :new.document_id FROM DUAL;
END;
/

DROP TRIGGER LOCUS_DOC_REF_TRIGGER;
--/
CREATE TRIGGER LOCUS_DOC_REF_TRIGGER
BEFORE INSERT ON locus_document_reference
FOR EACH ROW
BEGIN
SELECT doc_ref_seq.nextval INTO :new.document_reference_id FROM DUAL;
END;
/

DROP TRIGGER LOCUS_RELATION_TRIGGER;
--/
CREATE TRIGGER LOCUS_RELATION_TRIGGER
BEFORE INSERT ON locus_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER LOCUS_URL_TRIGGER;
--/
CREATE TRIGGER LOCUS_URL_TRIGGER
BEFORE INSERT ON locus_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER MUTANT_TRIGGER;
--/
CREATE TRIGGER MUTANT_TRIGGER
BEFORE INSERT ON mutant
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.mutant_id FROM DUAL;
END;
/

DROP TRIGGER MUTANT_ALIAS_TRIGGER;
--/
CREATE TRIGGER MUTANT_ALIAS_TRIGGER
BEFORE INSERT ON mutant_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER MUTANT_REL_TRIGGER;
--/
CREATE TRIGGER MUTANT_REL_TRIGGER
BEFORE INSERT ON mutant_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER OBSERVABLE_TRIGGER;
--/
CREATE TRIGGER OBSERVABLE_TRIGGER
BEFORE INSERT ON observable
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.observable_id FROM DUAL;
END;
/

DROP TRIGGER OBSERVABLE_ALIAS_TRIGGER;
--/
CREATE TRIGGER OBSERVABLE_ALIAS_TRIGGER
BEFORE INSERT ON observable_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER OBSERVABLE_REL_TRIGGER;
--/
CREATE TRIGGER OBSERVABLE_REL_TRIGGER
BEFORE INSERT ON observable_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER ORPHAN_TRIGGER;
--/
CREATE TRIGGER ORPHAN_TRIGGER
BEFORE INSERT ON orphan
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.orphan_id FROM DUAL;
END;
/

DROP TRIGGER ORPHAN_URL_TRIGGER;
--/
CREATE TRIGGER ORPHAN_URL_TRIGGER
BEFORE INSERT ON orphan_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER PHENOTYPE_TRIGGER;
--/
CREATE TRIGGER PHENOTYPE_TRIGGER
BEFORE INSERT ON phenotype
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.phenotype_id FROM DUAL;
END;
/

DROP TRIGGER POSTTRANSANNOTATION_TRIGGER;
--/
CREATE TRIGGER POSTTRANSANNOTATION_TRIGGER
BEFORE INSERT ON posttranslationalannotation
FOR EACH ROW
BEGIN
SELECT annotation_seq.nextval INTO :new.annotation_id FROM DUAL;
END;
/

DROP TRIGGER PROTEINDOMAIN_TRIGGER;
--/
CREATE TRIGGER PROTEINDOMAIN_TRIGGER
BEFORE INSERT ON proteindomain
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.proteindomain_id FROM DUAL;
END;
/

DROP TRIGGER PROTEINDOMAIN_URL_TRIGGER;
--/
CREATE TRIGGER PROTEINDOMAIN_URL_TRIGGER
BEFORE INSERT ON proteindomain_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER QUALIFIER_TRIGGER;
--/
CREATE TRIGGER QUALIFIER_TRIGGER
BEFORE INSERT ON qualifier
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.qualifier_id FROM DUAL;
END;
/

DROP TRIGGER QUALIFIER_ALIAS_TRIGGER;
--/
CREATE TRIGGER QUALIFIER_ALIAS_TRIGGER
BEFORE INSERT ON qualifier_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER QUALIFIER_REL_TRIGGER;
--/
CREATE TRIGGER QUALIFIER_REL_TRIGGER
BEFORE INSERT ON qualifier_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_ALIAS_TRIGGER;
--/
CREATE TRIGGER REFERENCE_ALIAS_TRIGGER
BEFORE INSERT ON reference_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_AUTHOR_TRIGGER;
--/
CREATE TRIGGER REFERENCE_AUTHOR_TRIGGER
BEFORE INSERT ON reference_author
FOR EACH ROW
BEGIN
SELECT reference_author_seq.nextval INTO :new.reference_author_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_DOC_TRIGGER;
--/
CREATE TRIGGER REFERENCE_DOC_TRIGGER
BEFORE INSERT ON reference_document
FOR EACH ROW
BEGIN
SELECT document_seq.nextval INTO :new.document_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_REFTYPE_TRIGGER;
--/
CREATE TRIGGER REFERENCE_REFTYPE_TRIGGER
BEFORE INSERT ON reference_reftype
FOR EACH ROW
BEGIN
SELECT reference_reftype_seq.nextval INTO :new.reference_reftype_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_RELATION_TRIGGER;
--/
CREATE TRIGGER REFERENCE_RELATION_TRIGGER
BEFORE INSERT ON reference_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER REFERENCE_URL_TRIGGER;
--/
CREATE TRIGGER REFERENCE_URL_TRIGGER
BEFORE INSERT ON reference_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER SEQUENCEFEATURE_TRIGGER;
--/
CREATE TRIGGER SEQUENCEFEATURE_TRIGGER
BEFORE INSERT ON sequencefeature
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.sequencefeature_id FROM DUAL;
END;
/

DROP TRIGGER SEQUENCEFEATURE_ALIAS_TRIGGER;
--/
CREATE TRIGGER SEQUENCEFEATURE_ALIAS_TRIGGER
BEFORE INSERT ON sequencefeature_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER SEQUENCEFEATURE_REL_TRIGGER;
--/
CREATE TRIGGER SEQUENCEFEATURE_REL_TRIGGER
BEFORE INSERT ON sequencefeature_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/

DROP TRIGGER SEQUENCEFEATURE_URL_TRIGGER;
--/
CREATE TRIGGER SEQUENCEFEATURE_URL_TRIGGER
BEFORE INSERT ON sequencefeature_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER STRAIN_DOC_TRIGGER;
--/
CREATE TRIGGER STRAIN_DOC_TRIGGER
BEFORE INSERT ON strain_document
FOR EACH ROW
BEGIN
SELECT document_seq.nextval INTO :new.document_id FROM DUAL;
END;
/

DROP TRIGGER STRAIN_DOC_REF_TRIGGER;
--/
CREATE TRIGGER STRAIN_DOC_REF_TRIGGER
BEFORE INSERT ON strain_document_reference
FOR EACH ROW
BEGIN
SELECT doc_ref_seq.nextval INTO :new.document_reference_id FROM DUAL;
END;
/

DROP TRIGGER STRAIN_URL_TRIGGER;
--/
CREATE TRIGGER STRAIN_URL_TRIGGER
BEFORE INSERT ON strain_url
FOR EACH ROW
BEGIN
SELECT url_seq.nextval INTO :new.url_id FROM DUAL;
END;
/

DROP TRIGGER TAXONOMY_TRIGGER;
--/
CREATE TRIGGER TAXONOMY_TRIGGER
BEFORE INSERT ON taxonomy
FOR EACH ROW
BEGIN
SELECT object_seq.nextval INTO :new.taxonomy_id FROM DUAL;
END;
/

DROP TRIGGER TAXONOMY_ALIAS_TRIGGER;
--/
CREATE TRIGGER TAXONOMY_ALIAS_TRIGGER
BEFORE INSERT ON taxonomy_alias
FOR EACH ROW
BEGIN
SELECT alias_seq.nextval INTO :new.alias_id FROM DUAL;
END;
/

DROP TRIGGER TAXONOMY_RELATION_TRIGGER;
--/
CREATE TRIGGER TAXONOMY_RELATION_TRIGGER
BEFORE INSERT ON taxonomy_relation
FOR EACH ROW
BEGIN
SELECT relation_seq.nextval INTO :new.relation_id FROM DUAL;
END;
/
