from django.test import TestCase
from django.urls import reverse

from common.tests import BaseViewTestMixin


class HomeViewTest(BaseViewTestMixin, TestCase):
    url = reverse("home")
    template = "core/home.html"
    page_name = "Home"
    expected_text = ["ClinVar Submission Service"]


class AboutViewTest(BaseViewTestMixin, TestCase):
    url = reverse("about")
    template = "core/about.html"
    page_name = "About"
    expected_text = ["ClinVar Submission Service", "CVSS", "ClinGen"]


class ContactViewTest(BaseViewTestMixin, TestCase):
    url = reverse("contact")
    template = "core/contact.html"
    page_name = "Contact"
    expected_text = ["email", "cvss@clinicalgenome.org"]


class HelpViewTest(BaseViewTestMixin, TestCase):
    url = reverse("help")
    template = "core/help.html"
    page_name = "Help"
    expected_text = ["email", "cvss@clinicalgenome.org"]
