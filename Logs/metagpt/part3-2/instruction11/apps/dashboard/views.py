from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Renders the dashboard page for authenticated users.
    """
    template_name = "dashboard.html"
    login_url = '/login/'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Add any additional context data here, e.g., user profile, stats, etc.
        context['user'] = user
        if hasattr(user, 'profile'):
            context['profile'] = user.profile
        else:
            context['profile'] = None
        return context