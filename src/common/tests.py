"""Houses code used commonly in tests."""

from django.test import Client


class BaseViewTestMixin:
    """Base mixin with common view tests."""

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)

    def test_page_name_in_response(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.page_name)

    def test_expected_text_in_response(self):
        response = self.client.get(self.url)
        for text in self.expected_text:
            self.assertContains(response, text)
