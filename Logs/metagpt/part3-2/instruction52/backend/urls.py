from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from documents.views import DocumentViewSet
from summaries.views import SummaryViewSet
from formulas.views import FormulaViewSet, FormulaResultViewSet

router = routers.DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'summaries', SummaryViewSet, basename='summary')
router.register(r'formulas', FormulaViewSet, basename='formula')
router.register(r'formula-results', FormulaResultViewSet, basename='formularesult')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Optionally, include authentication endpoints if using DRF's token or session auth
    path('api-auth/', include('rest_framework.urls')),
]