from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_report, name='generate_report'),
    path('detail/<int:report_id>/', views.report_detail, name='report_detail'),
    path('export/<int:report_id>/<str:format>/', views.export_report, name='export_report'),
]