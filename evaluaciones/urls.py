# evaluaciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade_list, name='grade_list'),
    
    # URLs de Carreras (actualizadas)
    path('carreras/', views.lista_carreras, name='lista_carreras'),
    path('carreras/agregar/', views.agregar_carrera, name='agregar_carrera'),
    path('carreras/editar/<int:carrera_id>/', views.editar_carrera, name='editar_carrera'),
    path('carreras/eliminar/<int:carrera_id>/', views.eliminar_carrera, name='eliminar_carrera'),
    path('carreras/detalle/<int:carrera_id>/', views.detalle_carrera, name='detalle_carrera'),
    
    # Otras URLs
    path('importar/', views.import_grades, name='import_grades'),
    path('acta/generar/', views.generate_transcript, name='generate_transcript'),
    path('acta/ver/<int:transcript_id>/', views.view_transcript, name='view_transcript'),
    path('carreras/agregar-materia/<int:carrera_id>/', views.agregar_materia, name='agregar_materia'),
    path('carreras/eliminar-materia/<int:materia_id>/', views.eliminar_materia, name='eliminar_materia'),
    path('materia/<int:materia_id>/editar/', views.editar_materia, name='editar_materia'),
    path('materia/<int:materia_id>/cambiar-estado/', views.cambiar_estado_materia, name='cambiar_estado_materia'),
    path('materia/<int:materia_id>/datos/', views.obtener_datos_materia, name='obtener_datos_materia'),
    # evaluaciones/urls.py
    path('materia/<int:materia_id>/debug/', views.debug_materia, name='debug_materia'),
    path('carreras/asignar-materias/<int:carrera_id>/', views.asignar_materias_unidades_sin_asignar, name='asignar_materias_unidades'),
]