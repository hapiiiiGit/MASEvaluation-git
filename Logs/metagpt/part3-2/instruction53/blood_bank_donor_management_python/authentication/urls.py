from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('password-reset-request/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
]