from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    # The router will handle /api/auth/register, /api/auth/login, /api/auth/logout
]

urlpatterns += router.urls