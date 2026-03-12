from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CoreDataViewSet

router = DefaultRouter()
router.register(r'data', CoreDataViewSet, basename='coredata')

urlpatterns = [
    # The router will handle /api/data/ endpoints (list, create, retrieve, update, destroy)
]

urlpatterns += router.urls