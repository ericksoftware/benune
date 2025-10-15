# alumnos/urls.py - ACTUALIZADO
from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('nuevo/', views.student_create, name='student_create'),
    path('detalle/<int:student_id>/', views.student_detail, name='student_detail'),
    path('editar/<int:student_id>/', views.student_edit, name='student_edit'),
    path('eliminar/<int:student_id>/', views.student_delete, name='student_delete'),
    path('calificaciones/<int:student_id>/', views.student_update_grades, name='student_update_grades'), 
]