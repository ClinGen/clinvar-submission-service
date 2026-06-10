from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Returns the home page."""
    return render(request, "core/home.html")


def about(request: HttpRequest) -> HttpResponse:
    """Returns the about page."""
    return render(request, "core/about.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Returns the contact page."""
    return render(request, "core/contact.html")


def help_(request: HttpRequest) -> HttpResponse:
    """Returns the help page."""
    return render(request, "core/help.html")
