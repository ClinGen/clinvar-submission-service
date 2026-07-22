from django.urls import path

from classification import views

urlpatterns = [
    path("list/", views.ClassificationList.as_view(), name="classification-list"),
]
