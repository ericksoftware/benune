from django.contrib import admin
from .models import Materia, Calificacion, ActaEvaluacion

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'clave', 'licenciatura', 'semestre', 'creditos']
    list_filter = ['licenciatura', 'semestre']
    search_fields = ['nombre', 'clave']
    ordering = ['semestre', 'nombre']

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'materia', 'calificacion', 'periodo']
    list_filter = ['materia', 'periodo', 'materia__licenciatura']
    search_fields = ['alumno__nombre', 'alumno__apellido_paterno', 'materia__nombre']
    ordering = ['-fecha_registro']

@admin.register(ActaEvaluacion)
class ActaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['materia', 'licenciatura', 'semestre', 'grupo', 'periodo', 'estado']
    list_filter = ['licenciatura', 'semestre', 'estado', 'periodo']
    search_fields = ['materia__nombre', 'grupo']
    ordering = ['-fecha_generacion']