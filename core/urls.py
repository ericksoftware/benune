# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Redirección principal
    path('', views.home_redirect, name='home'),
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
]