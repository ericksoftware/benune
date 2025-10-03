from django.contrib import admin
from .models import Licenciatura, Materia, Calificacion, PromedioPeriodo, ActaEvaluacion

@admin.register(Licenciatura)
class LicenciaturaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'plan', 'numero_semestres', 'activa', 'fecha_creacion']
    list_filter = ['activa', 'plan', 'numero_semestres']
    search_fields = ['codigo', 'nombre']
    list_editable = ['activa']
    ordering = ['nombre']

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'licenciatura', 'semestre', 'creditos', 'activa']
    list_filter = ['licenciatura', 'semestre', 'activa']
    search_fields = ['codigo', 'nombre', 'licenciatura__nombre']
    list_editable = ['activa']
    ordering = ['licenciatura', 'semestre', 'codigo']

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'materia', 'calificacion', 'periodo', 'fecha_registro']
    list_filter = ['periodo', 'materia__licenciatura', 'materia__semestre']
    search_fields = ['alumno__matricula', 'alumno__nombre', 'materia__codigo']
    ordering = ['alumno', 'periodo']

@admin.register(PromedioPeriodo)
class PromedioPeriodoAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'periodo', 'promedio_general', 'materias_cursadas', 'fecha_calculo']
    list_filter = ['periodo']
    search_fields = ['alumno__matricula', 'alumno__nombre']
    ordering = ['alumno', 'periodo']

@admin.register(ActaEvaluacion)
class ActaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['materia', 'grupo', 'periodo', 'estado', 'fecha_emision', 'promedio_grupo']
    list_filter = ['estado', 'periodo', 'licenciatura', 'semestre']
    search_fields = ['materia__codigo', 'materia__nombre', 'grupo']
    ordering = ['-fecha_generacion']