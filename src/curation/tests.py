from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from curation.models import Curation, Disease, Variant

LIST_URL = reverse("curation-list")


class CurationListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="submitter", password="password")

    def test_authenticated_user_gets_200_and_correct_template(self):
        self.client.login(username="submitter", password="password")
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "curation/list.html")

    def test_unauthenticated_request_redirects_to_login(self):
        response = self.client.get(LIST_URL)
        self.assertRedirects(
            response, f"/accounts/login/?next={LIST_URL}", fetch_redirect_response=False
        )

    def test_curations_appear_in_response(self):
        self.client.login(username="submitter", password="password")
        variant = Variant.objects.create(
            car_id="CA999",
            gene_symbol="FOO",
            reference_sequence="BAR",
            hgvs="BAZ",
        )
        disease = Disease.objects.create(id_type="MONDO", id_value="MONDO:12345")
        Curation.objects.create(
            variant=variant,
            disease=disease,
            affiliation="12345",
            local_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            linking_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            germline_classification="Pathogenic",
            mode_of_inheritance="Autosomal dominant inheritance",
            collection_method="curation",
            allele_origin="germline",
            affected_status="yes",
            source_app="vci_v3",
            schema_version="1.0",
            raw_payload={},
        )
        response = self.client.get(LIST_URL)

        self.assertContains(response, "ID")
        self.assertContains(response, "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        self.assertContains(response, "Variant")
        self.assertContains(response, "CA999")

        self.assertContains(response, "Disease")
        self.assertContains(response, "MONDO:12345")

        self.assertContains(response, "Classification")
        self.assertContains(response, "Pathogenic")

        self.assertContains(response, "Affiliation")
        self.assertContains(response, "12345")

        self.assertContains(response, "Status")
        self.assertContains(response, "Pending")

        self.assertContains(response, "Received")
