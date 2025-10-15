# alumnos/admin.py - ACTUALIZADO
from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 
        'nombre_completo', 
        'carrera', 
        'semestre_actual', 
        'estado',
        'fecha_registro'
    ]
    list_filter = [
        'estado', 
        'turno', 
        'sexo', 
        'carrera',
        'fecha_registro'
    ]
    search_fields = [
        'matricula', 
        'nombre', 
        'apellido_paterno', 
        'apellido_materno',
        'curp'
    ]
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    fieldsets = [
        ('Información Básica', {
            'fields': [
                'matricula', 'curp', 'rfc', 
                'nombre', 'apellido_paterno', 'apellido_materno'
            ]
        }),
        ('Información Personal', {
            'fields': [
                'municipio_nacimiento', 'fecha_nacimiento', 'sexo'
            ]
        }),
        ('Información Académica Previa', {
            'fields': [
                'institucion_procedencia', 'municipio_institucion', 'clave_escuela',
                'fecha_terminacion_prepa', 'promedio_prepa', 'constancia_terminacion'
            ]
        }),
        ('Información Académica Actual', {
            'fields': [
                'carrera', 'promedio_semestre_anterior', 'semestre_actual',
                'turno', 'plan', 'estado'
            ]
        }),
        ('Información de Contacto', {
            'fields': [
                'email_institucional', 'password_email_institucional',
                'email_personal', 'telefono'
            ]
        }),
        ('Metadata', {
            'fields': ['fecha_registro', 'fecha_actualizacion'],
            'classes': ['collapse']
        })
    ]