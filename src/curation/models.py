import uuid

from django.db import models
from simple_history.models import HistoricalRecords


class Variant(models.Model):
    car_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    gene_symbol = models.CharField(max_length=50)
    reference_sequence = models.CharField(max_length=100)
    hgvs = models.TextField()
    alternate_designations = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.hgvs


class Disease(models.Model):
    id_type = models.CharField(max_length=50)
    id_value = models.CharField(max_length=100)
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
        return f"{self.id_type}:{self.id_value}"


class Publication(models.Model):
    pubmed_id = models.CharField(max_length=20, null=True, blank=True)
    doi = models.CharField(max_length=200, null=True, blank=True)
    title = models.TextField(blank=True)
    authors = models.JSONField(default=list)
    publication_year = models.IntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.pubmed_id or self.doi or self.title or str(self.pk)


class Batch(models.Model):
    class Status(models.TextChoices):
        CREATED = "CRE", "Created"
        SUBMITTED = "SUB", "Submitted"
        PROCESSED = "PRO", "Processed"
        ERROR = "ERR", "Error"

    name = models.CharField(max_length=200, blank=True)
    submission_id = models.CharField(max_length=20, null=True, blank=True)
    payload = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status, default=Status.CREATED)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name or self.submission_id or str(self.pk)


class Curation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PND", "Pending"
        IN_BATCH = "BAT", "In Batch"
        SUBMITTED = "SUB", "Submitted"
        PROCESSED = "PRO", "Processed"
        ERROR = "ERR", "Error"

    variant = models.ForeignKey(
        Variant, on_delete=models.PROTECT, related_name="curations"
    )
    disease = models.ForeignKey(
        Disease, on_delete=models.PROTECT, related_name="curations"
    )
    publications = models.ManyToManyField(
        Publication, blank=True, related_name="curations"
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curations",
    )
    local_id = models.UUIDField(default=uuid.uuid4)
    linking_id = models.UUIDField(default=uuid.uuid4)
    germline_classification = models.CharField(max_length=100)
    mode_of_inheritance = models.CharField(max_length=200)
    date_last_evaluated = models.DateField(null=True, blank=True)
    comment_on_classification = models.TextField(blank=True)
    collection_method = models.CharField(max_length=100)
    allele_origin = models.CharField(max_length=100)
    affected_status = models.CharField(max_length=100)
    scv = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=3, choices=Status, default=Status.PENDING)
    source_app = models.CharField(max_length=50)
    schema_version = models.CharField(max_length=20)
    raw_payload = models.JSONField()
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.local_id)
