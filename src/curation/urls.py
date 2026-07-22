from django.urls import path

from curation import views

urlpatterns = [
    path("list/", views.CurationList.as_view(), name="curation-list"),
]
