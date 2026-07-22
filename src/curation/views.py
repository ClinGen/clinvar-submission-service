from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from curation.models import Curation


class CurationList(LoginRequiredMixin, ListView):
    template_name = "curation/list.html"
    context_object_name = "curations"

    def get_queryset(self):
        return Curation.objects.select_related("variant", "disease").order_by(
            "-added_at"
        )
