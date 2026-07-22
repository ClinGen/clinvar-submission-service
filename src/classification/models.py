import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from classification.constants.models import (
    BatchMaxLength,
    BatchStatus,
    ClassificationMaxLength,
    ClassificationStatus,
    DiseaseMaxLength,
    PublicationMaxLength,
    VariantMaxLength,
)


class Variant(models.Model):
    car_id = models.CharField(
        max_length=VariantMaxLength.CAR_ID, unique=True, null=True, blank=True
    )
    gene_symbol = models.CharField(max_length=VariantMaxLength.GENE_SYMBOL)
    reference_sequence = models.CharField(
        max_length=VariantMaxLength.REFERENCE_SEQUENCE
    )
    hgvs = models.TextField()
    alternate_designations = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.hgvs


class Disease(models.Model):
    id_type = models.CharField(max_length=DiseaseMaxLength.ID_TYPE)
    id_value = models.CharField(max_length=DiseaseMaxLength.ID_VALUE)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_type", "id_value"], name="unique_disease_id"
            )
        ]

    def __str__(self):
        return f"{self.id_value}"


class Publication(models.Model):
    pubmed_id = models.CharField(
        max_length=PublicationMaxLength.PUBMED_ID, null=True, blank=True
    )
    doi = models.CharField(max_length=PublicationMaxLength.DOI, null=True, blank=True)
    title = models.TextField(blank=True)
    authors = models.JSONField(default=list)
    publication_year = models.IntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.pubmed_id or self.doi or self.title or str(self.pk)


class Batch(models.Model):
    Status = BatchStatus

    name = models.CharField(max_length=BatchMaxLength.NAME, blank=True)
    submission_id = models.CharField(
        max_length=BatchMaxLength.SUBMISSION_ID, null=True, blank=True
    )
    payload = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=BatchMaxLength.STATUS,
        choices=BatchStatus,
        default=BatchStatus.CREATED,
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name or self.submission_id or str(self.pk)


class Classification(models.Model):
    Status = ClassificationStatus

    variant = models.ForeignKey(
        Variant, on_delete=models.PROTECT, related_name="classifications"
    )
    disease = models.ForeignKey(
        Disease, on_delete=models.PROTECT, related_name="classifications"
    )
    publications = models.ManyToManyField(
        Publication, blank=True, related_name="classifications"
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classifications",
    )
    local_id = models.UUIDField(default=uuid.uuid4)
    linking_id = models.UUIDField(default=uuid.uuid4)
    germline_classification = models.CharField(
        max_length=ClassificationMaxLength.GERMLINE_CLASSIFICATION
    )
    mode_of_inheritance = models.CharField(
        max_length=ClassificationMaxLength.MODE_OF_INHERITANCE
    )
    date_last_evaluated = models.DateField(null=True, blank=True)
    comment_on_classification = models.TextField(blank=True)
    collection_method = models.CharField(max_length=ClassificationMaxLength.COLLECTION_METHOD)
    allele_origin = models.CharField(max_length=ClassificationMaxLength.ALLELE_ORIGIN)
    affected_status = models.CharField(max_length=ClassificationMaxLength.AFFECTED_STATUS)
    affiliation = models.CharField(max_length=ClassificationMaxLength.AFFILIATION, default="")
    scv = models.CharField(max_length=ClassificationMaxLength.SCV, null=True, blank=True)
    status = models.CharField(
        max_length=ClassificationMaxLength.STATUS,
        choices=ClassificationStatus,
        default=ClassificationStatus.PENDING,
    )
    source_app = models.CharField(max_length=ClassificationMaxLength.SOURCE_APP)
    schema_version = models.CharField(max_length=ClassificationMaxLength.SCHEMA_VERSION)
    raw_payload = models.JSONField()
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.local_id)
