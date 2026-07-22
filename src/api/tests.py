import uuid

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from classification.models import Classification, Disease, Publication, Variant

CREATE_URL = "/api/v1/classification/create/"

VALID_PAYLOAD = {
    "variant": {
        "car_id": "CA123",
        "gene_symbol": "FOO",
        "reference_sequence": "BAR",
        "hgvs": "BAZ",
        "alternate_designations": "foobar_alt_1",
    },
    "disease": {
        "id_type": "MONDO",
        "id_value": "MONDO:0000001",
    },
    "publications": [
        {
            "pubmed_id": "11111111",
            "doi": None,
            "title": "Foobar variant study",
            "authors": ["Foo A", "Bar B"],
            "publication_year": 2020,
        }
    ],
    "affiliation": "10000",
    "source_app": "foobar-app",
    "schema_version": "1.0",
    "raw_payload": {"foo": "bar"},
    "local_id": "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
    "linking_id": "bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb",
    "germline_classification": "Pathogenic",
    "mode_of_inheritance": "Autosomal dominant",
    "date_last_evaluated": "2025-01-01",
    "comment_on_classification": "Foobar comment on classification.",
    "collection_method": "literature only",
    "allele_origin": "germline",
    "affected_status": "yes",
}


class ClassificationCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        _, key = APIKey.objects.create_key(name="test-vci")
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")

    def test_create_returns_201_for_valid_payload(self):
        response = self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["local_id"], VALID_PAYLOAD["local_id"])
        self.assertEqual(response.data["status"], "pending")

    def test_create_stores_classification_variant_disease_publication(self):
        self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(Classification.objects.count(), 1)
        self.assertEqual(Variant.objects.count(), 1)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(Publication.objects.count(), 1)
        classification = Classification.objects.get()
        self.assertEqual(classification.publications.count(), 1)

    def test_create_reuses_existing_variant_by_car_id(self):
        Variant.objects.create(
            car_id="CA123",
            gene_symbol="FOO",
            reference_sequence="BAR",
            hgvs="BAZ",
        )
        self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(Variant.objects.count(), 1)

    def test_create_reuses_existing_disease(self):
        Disease.objects.create(id_type="MONDO", id_value="MONDO:0000001")
        self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(Disease.objects.count(), 1)

    def test_create_returns_409_for_duplicate_local_id(self):
        self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        response = self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 409)

    def test_create_returns_403_without_api_key(self):
        unauthed = APIClient()
        response = unauthed.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 403)

    def test_create_returns_400_for_missing_required_fields(self):
        response = self.client.post(CREATE_URL, {"affiliation": "10000"}, format="json")
        self.assertEqual(response.status_code, 400)


class ClassificationUpdateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        _, key = APIKey.objects.create_key(name="test-vci")
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")
        create_response = self.client.post(CREATE_URL, VALID_PAYLOAD, format="json")
        self.local_id = create_response.data["local_id"]
        self.update_url = f"/api/v1/classification/{self.local_id}/update/"

    @staticmethod
    def _updated_payload():
        payload = dict(VALID_PAYLOAD)
        payload["germline_classification"] = "Likely pathogenic"
        return payload

    def test_update_returns_200_for_valid_pending_classification(self):
        response = self.client.put(
            self.update_url, self._updated_payload(), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["local_id"], self.local_id)
        self.assertEqual(response.data["status"], "pending")
        classification = Classification.objects.get(local_id=self.local_id)
        self.assertEqual(classification.germline_classification, "Likely pathogenic")

    def test_update_returns_404_for_nonexistent_local_id(self):
        missing_id = uuid.uuid4()
        response = self.client.put(
            f"/api/v1/classification/{missing_id}/update/",
            self._updated_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_returns_409_when_status_is_in_batch(self):
        Classification.objects.filter(local_id=self.local_id).update(
            status=Classification.Status.IN_BATCH
        )
        response = self.client.put(
            self.update_url, self._updated_payload(), format="json"
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("In Batch", response.data["detail"])

    def test_update_returns_409_when_status_is_submitted(self):
        Classification.objects.filter(local_id=self.local_id).update(
            status=Classification.Status.SUBMITTED
        )
        response = self.client.put(
            self.update_url, self._updated_payload(), format="json"
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("Submitted", response.data["detail"])

    def test_update_returns_403_without_api_key(self):
        unauthed = APIClient()
        response = unauthed.put(self.update_url, self._updated_payload(), format="json")
        self.assertEqual(response.status_code, 403)
