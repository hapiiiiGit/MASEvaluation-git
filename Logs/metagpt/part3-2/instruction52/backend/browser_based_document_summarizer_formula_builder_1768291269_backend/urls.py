from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('urls')),  # Central API router (backend/urls.py)
    path('api-auth/', include('rest_framework.urls')),
]