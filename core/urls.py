# core/urls.py - ACTUALIZADO
from django.urls import path
from . import views

urlpatterns = [
    # Redirección principal
    path('', views.home_redirect, name='home'),
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Página de acceso prohibido
    path('forbidden/', views.forbidden_view, name='forbidden'),
]