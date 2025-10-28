# usuarios/urls.py - NUEVO ARCHIVO
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('nuevo/', views.user_create, name='user_create'),
    path('detalle/<int:user_id>/', views.user_detail, name='user_detail'),
    path('editar/<int:user_id>/', views.user_edit, name='user_edit'),
    path('eliminar/<int:user_id>/', views.user_delete, name='user_delete'),
]