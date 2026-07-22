from rest_framework import serializers

from curation.constants.models import (
    CurationMaxLength,
    DiseaseMaxLength,
    PublicationMaxLength,
    VariantMaxLength,
)
from curation.models import Curation, Disease, Publication, Variant


class VariantSerializer(serializers.Serializer):
    car_id = serializers.CharField(
        max_length=VariantMaxLength.CAR_ID,
        required=False,
        allow_null=True,
        default=None,
    )
    gene_symbol = serializers.CharField(max_length=VariantMaxLength.GENE_SYMBOL)
    reference_sequence = serializers.CharField(
        max_length=VariantMaxLength.REFERENCE_SEQUENCE
    )
    hgvs = serializers.CharField()
    alternate_designations = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class DiseaseSerializer(serializers.Serializer):
    id_type = serializers.CharField(max_length=DiseaseMaxLength.ID_TYPE)
    id_value = serializers.CharField(max_length=DiseaseMaxLength.ID_VALUE)


class PublicationSerializer(serializers.Serializer):
    pubmed_id = serializers.CharField(
        max_length=PublicationMaxLength.PUBMED_ID,
        required=False,
        allow_null=True,
        default=None,
    )
    doi = serializers.CharField(
        max_length=PublicationMaxLength.DOI,
        required=False,
        allow_null=True,
        default=None,
    )
    title = serializers.CharField(required=False, allow_blank=True, default="")
    authors = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    publication_year = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )


class CurationSerializer(serializers.Serializer):
    variant = VariantSerializer()
    disease = DiseaseSerializer()
    publications = PublicationSerializer(many=True, required=False, default=list)
    affiliation = serializers.CharField(max_length=CurationMaxLength.AFFILIATION)
    source_app = serializers.CharField(max_length=CurationMaxLength.SOURCE_APP)
    schema_version = serializers.CharField(max_length=CurationMaxLength.SCHEMA_VERSION)
    raw_payload = serializers.JSONField()
    local_id = serializers.UUIDField()
    linking_id = serializers.UUIDField()
    germline_classification = serializers.CharField(
        max_length=CurationMaxLength.GERMLINE_CLASSIFICATION
    )
    mode_of_inheritance = serializers.CharField(
        max_length=CurationMaxLength.MODE_OF_INHERITANCE
    )
    date_last_evaluated = serializers.DateField(
        required=False, allow_null=True, default=None
    )
    comment_on_classification = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    collection_method = serializers.CharField(
        max_length=CurationMaxLength.COLLECTION_METHOD
    )
    allele_origin = serializers.CharField(max_length=CurationMaxLength.ALLELE_ORIGIN)
    affected_status = serializers.CharField(
        max_length=CurationMaxLength.AFFECTED_STATUS
    )

    def _upsert_variant(self, data):
        if data.get("car_id"):
            variant, _ = Variant.objects.update_or_create(
                car_id=data["car_id"],
                defaults={k: v for k, v in data.items() if k != "car_id"},
            )
        else:
            variant, _ = Variant.objects.update_or_create(
                hgvs=data["hgvs"],
                reference_sequence=data["reference_sequence"],
                defaults={
                    k: v
                    for k, v in data.items()
                    if k not in ("hgvs", "reference_sequence")
                },
            )
        return variant

    def _get_or_create_disease(self, data):
        disease, _ = Disease.objects.get_or_create(
            id_type=data["id_type"],
            id_value=data["id_value"],
        )
        return disease

    def _upsert_publication(self, data):
        if data.get("pubmed_id"):
            pub, _ = Publication.objects.update_or_create(
                pubmed_id=data["pubmed_id"],
                defaults={k: v for k, v in data.items() if k != "pubmed_id"},
            )
        else:
            pub, _ = Publication.objects.update_or_create(
                doi=data["doi"],
                defaults={k: v for k, v in data.items() if k != "doi"},
            )
        return pub

    def create(self, validated_data):
        variant_data = validated_data.pop("variant")
        disease_data = validated_data.pop("disease")
        publications_data = validated_data.pop("publications", [])

        variant = self._upsert_variant(variant_data)
        disease = self._get_or_create_disease(disease_data)
        pubs = [self._upsert_publication(p) for p in publications_data]

        curation = Curation.objects.create(
            variant=variant,
            disease=disease,
            status=Curation.Status.PENDING,
            **validated_data,
        )
        curation.publications.set(pubs)
        return curation

    def update(self, instance, validated_data):
        variant_data = validated_data.pop("variant")
        disease_data = validated_data.pop("disease")
        publications_data = validated_data.pop("publications", [])

        instance.variant = self._upsert_variant(variant_data)
        instance.disease = self._get_or_create_disease(disease_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        pubs = [self._upsert_publication(p) for p in publications_data]
        instance.publications.set(pubs)
        return instance
