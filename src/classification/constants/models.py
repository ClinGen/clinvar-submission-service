from django.db import models


class VariantMaxLength:
    CAR_ID = 50
    GENE_SYMBOL = 50
    REFERENCE_SEQUENCE = 100


class DiseaseMaxLength:
    ID_TYPE = 50
    ID_VALUE = 100


class PublicationMaxLength:
    PUBMED_ID = 20
    DOI = 200


class BatchMaxLength:
    NAME = 200
    SUBMISSION_ID = 20
    STATUS = 20


class ClassificationMaxLength:
    AFFILIATION = 5
    SOURCE_APP = 50
    SCHEMA_VERSION = 20
    GERMLINE_CLASSIFICATION = 100
    MODE_OF_INHERITANCE = 200
    COLLECTION_METHOD = 100
    ALLELE_ORIGIN = 100
    AFFECTED_STATUS = 100
    SCV = 30
    STATUS = 3


class BatchStatus(models.TextChoices):
    CREATED = "CRE", "Created"
    SUBMITTED = "SUB", "Submitted"
    PROCESSED = "PRO", "Processed"
    ERROR = "ERR", "Error"


class ClassificationStatus(models.TextChoices):
    PENDING = "PND", "Pending"
    IN_BATCH = "BAT", "In Batch"
    SUBMITTED = "SUB", "Submitted"
    PROCESSED = "PRO", "Processed"
    ERROR = "ERR", "Error"
