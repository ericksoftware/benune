# evaluaciones/admin.py
from django.contrib import admin
from .models import Carrera, Unidad, Materia, Calificacion, PromedioPeriodo, ActaEvaluacion

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'tipo_carrera', 'codigo', 'numero_semestres', 'plan', 'activa']
    list_filter = ['tipo_carrera', 'activa', 'plan']
    search_fields = ['nombre', 'codigo']
    list_editable = ['activa']
    ordering = ['id']

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'carrera', 'numero', 'nombre', 'materia_asignada', 'estado']
    list_filter = ['carrera']  # QUITAR 'materia' de list_filter
    search_fields = ['codigo', 'nombre', 'carrera__nombre']
    ordering = ['carrera', 'numero']
    
    def materia_asignada(self, obj):
        """Obtener la materia asignada a esta unidad"""
        if obj.materias.exists():
            return obj.materias.first().nombre
        return "Sin asignar"
    materia_asignada.short_description = 'Materia Asignada'
    
    def estado(self, obj):
        if obj.materias.exists():
            return "Ocupada"
        return "Disponible"
    estado.short_description = 'Estado'

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'carrera', 'semestre', 'unidades_asignadas', 'creditos', 'horas', 'activa']
    list_filter = ['carrera', 'semestre', 'activa']
    search_fields = ['nombre', 'carrera__nombre']
    filter_horizontal = ['unidades']  # Agregar filter_horizontal para ManyToMany
    list_editable = ['activa']
    ordering = ['carrera', 'semestre', 'nombre']
    
    def unidades_asignadas(self, obj):
        unidades = obj.unidades.all()
        if unidades:
            return ", ".join([unidad.codigo for unidad in unidades])
        return "Sin unidades"
    unidades_asignadas.short_description = 'Unidades Asignadas'

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'materia', 'calificacion', 'periodo', 'fecha_registro']
    list_filter = ['periodo', 'materia__carrera', 'materia__semestre']
    search_fields = ['alumno__matricula', 'alumno__nombre', 'materia__nombre']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    ordering = ['-fecha_registro']

@admin.register(PromedioPeriodo)
class PromedioPeriodoAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'periodo', 'promedio_general', 'total_materias', 'materias_aprobadas']
    list_filter = ['periodo']
    search_fields = ['alumno__matricula', 'alumno__nombre']
    readonly_fields = ['fecha_calculo']
    ordering = ['alumno', 'periodo']

@admin.register(ActaEvaluacion)
class ActaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['materia', 'carrera', 'semestre', 'grupo', 'periodo', 'estado', 'fecha_generacion']
    list_filter = ['carrera', 'semestre', 'estado', 'periodo']
    search_fields = ['materia__nombre', 'grupo']
    readonly_fields = ['fecha_generacion']
    ordering = ['-fecha_generacion']