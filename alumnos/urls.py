# alumnos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('detalle/<int:student_id>/', views.student_detail, name='student_detail'),
]