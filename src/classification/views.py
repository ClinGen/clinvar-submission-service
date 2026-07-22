from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from classification.models import Classification


class ClassificationList(LoginRequiredMixin, ListView):
    template_name = "classification/list.html"
    context_object_name = "classifications"

    def get_queryset(self):
        return Classification.objects.select_related("variant", "disease").order_by(
            "-added_at"
        )
