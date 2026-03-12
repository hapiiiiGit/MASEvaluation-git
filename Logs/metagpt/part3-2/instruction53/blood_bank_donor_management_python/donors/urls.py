from django.urls import path
from . import views

urlpatterns = [
    path('', views.donor_list, name='donor_list'),
    path('donor/<str:donor_id>/', views.donor_detail, name='donor_detail'),
    path('donor/create/', views.donor_create, name='donor_create'),
    path('donor/edit/<str:donor_id>/', views.donor_edit, name='donor_edit'),
    path('donor/delete/<str:donor_id>/', views.donor_delete, name='donor_delete'),
]