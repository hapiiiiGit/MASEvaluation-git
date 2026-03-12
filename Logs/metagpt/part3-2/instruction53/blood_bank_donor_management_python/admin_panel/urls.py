from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]