import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno

# Datos de alumnos de prueba
alumnos_data = [
    {
        'curp': 'AUME890823MBCGNL07',
        'nombre': 'ELLEN LIVIERE',
        'apellido_paterno': 'AGUILAR',
        'apellido_materno': 'MUNGUIA',
        'fecha_nacimiento': date(1989, 8, 23),
        'sexo': 'MUJER',
        'municipio_estado_nacimiento': 'MEXICALI, B.C.',
        'licenciatura': 'EDUCACION_ESPECIAL',
        'semestre_actual': 1,
        'turno': 'MATUTINO',
        'promedio_prepa': 9.5,
        'institucion_procedencia': 'COLEGIO DE ESTUDIOS CIENTIFICOS Y TECNOLOGICOS',
        'correo_particular': 'liviere.aguilar@gmail.com',
        'numero_celular': '6861956063'
    },
    {
        'curp': 'AUVA820219HBCGLR07',
        'nombre': 'ARMANDO MAURICIO',
        'apellido_paterno': 'AGUIRRE',
        'apellido_materno': 'VILLANUEVA',
        'fecha_nacimiento': date(1982, 2, 19),
        'sexo': 'HOMBRE',
        'municipio_estado_nacimiento': 'MEXICALI B.C.',
        'licenciatura': 'EDUCACION_ESPECIAL',
        'semestre_actual': 1,
        'turno': 'MATUTINO',
        'promedio_prepa': 7.0,
        'institucion_procedencia': 'COLEGIO DE BACHILLERES',
        'correo_particular': '',
        'numero_celular': '6863389692'
    },
    {
        'curp': 'AAGJ061228MBCLLRA7',
        'nombre': 'JURIDIA VANESSA',
        'apellido_paterno': 'ALVAREZ',
        'apellido_materno': 'GALLEGO',
        'fecha_nacimiento': date(2006, 12, 28),
        'sexo': 'MUJER',
        'municipio_estado_nacimiento': 'MEXICALI B.C.',
        'licenciatura': 'EDUCACION_ESPECIAL',
        'semestre_actual': 1,
        'turno': 'MATUTINO',
        'promedio_prepa': 9.3,
        'institucion_procedencia': 'COLEGIO DE BACHILLERES',
        'correo_particular': 'vanessa1228alvarez@gmail.com',
        'numero_celular': '6861950291'
    }
]

for alumno_data in alumnos_data:
    if not Alumno.objects.filter(curp=alumno_data['curp']).exists():
        alumno = Alumno.objects.create(**alumno_data)
        print(f"Alumno creado: {alumno.nombre_completo}")

print("Alumnos de prueba creados exitosamente!")