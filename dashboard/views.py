from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We can add quick placeholders / metrics for Sprint 1
        context['page_title'] = "Health Dashboard"
        context['recent_activities'] = [
            {"date": "Just now", "activity": "Logged in to MedIntel System"},
        ]
        return context
