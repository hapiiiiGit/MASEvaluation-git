from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# Home, login, and register views using Django's built-in auth forms and TemplateView
urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('apps.users.urls')),   # /api/auth/
    path('api/', include('apps.core.urls')),    # /api/data/

    # Dashboard
    path('', include('apps.dashboard.urls')),   # /dashboard/

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Login/Logout/Register (using Django's built-in views for forms)
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),  # Registration handled via API or custom view
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)