from django.urls import path

from api import views

urlpatterns = [
    path("health/", views.health),
    path("v1/classification/create/", views.ClassificationCreateView.as_view()),
    path("v1/classification/<uuid:local_id>/update/", views.ClassificationUpdateView.as_view()),
]
