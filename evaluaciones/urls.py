# evaluaciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade_list, name='grade_list'),
    path('importar/', views.import_grades, name='import_grades'),
    path('acta/generar/', views.generate_transcript, name='generate_transcript'),
    path('acta/ver/<int:transcript_id>/', views.view_transcript, name='view_transcript'),
]