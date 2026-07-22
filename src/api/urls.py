from django.urls import path

from api import views

urlpatterns = [
    path("health/", views.health),
    path("v1/curation/create/", views.CurationCreateView.as_view()),
    path("v1/curation/<uuid:local_id>/update/", views.CurationUpdateView.as_view()),
]
