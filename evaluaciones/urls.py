# evaluaciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade_list, name='grade_list'),
    path('licenciaturas/', views.lista_licenciaturas, name='lista_licenciaturas'),
    path('licenciaturas/agregar/', views.agregar_licenciatura, name='agregar_licenciatura'),
    path('licenciaturas/editar/<int:licenciatura_id>/', views.editar_licenciatura, name='editar_licenciatura'),
    path('licenciaturas/eliminar/<int:licenciatura_id>/', views.eliminar_licenciatura, name='eliminar_licenciatura'),
    path('licenciaturas/detalle/<int:licenciatura_id>/', views.detalle_licenciatura, name='detalle_licenciatura'),
    path('importar/', views.import_grades, name='import_grades'),
    path('acta/generar/', views.generate_transcript, name='generate_transcript'),
    path('acta/ver/<int:transcript_id>/', views.view_transcript, name='view_transcript'),
    path('licenciaturas/agregar-materia/<int:licenciatura_id>/', views.agregar_materia, name='agregar_materia'),
    path('licenciaturas/eliminar-materia/<int:materia_id>/', views.eliminar_materia, name='eliminar_materia'),
    path('materia/<int:materia_id>/editar/', views.editar_materia, name='editar_materia'),
    path('materia/<int:materia_id>/cambiar-estado/', views.cambiar_estado_materia, name='cambiar_estado_materia'),
    path('materia/<int:materia_id>/datos/', views.obtener_datos_materia, name='obtener_datos_materia'),
]