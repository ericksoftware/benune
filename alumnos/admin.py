# alumnos/admin.py
from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['matricula', 'nombre_completo', 'curp', 'licenciatura', 'semestre_actual', 'turno', 'sexo']
    list_filter = ['licenciatura', 'semestre_actual', 'turno', 'sexo']  # ← 'sexo' está bien
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'curp', 'matricula']
    ordering = ['apellido_paterno', 'apellido_materno', 'nombre']