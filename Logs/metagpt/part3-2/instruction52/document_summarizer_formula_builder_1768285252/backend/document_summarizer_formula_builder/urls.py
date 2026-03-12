"""
URL configuration for document_summarizer_formula_builder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('documents.urls')),
    path('api/', include('formulas.urls')),
    path('api/', include('users.urls')),
]