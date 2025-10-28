# create_initial_data.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from evaluaciones.models import Licenciatura, Materia
from usuarios.models import Usuario

print("🧪 Creando datos iniciales de prueba...")

# Crear licenciatura
lic, created = Licenciatura.objects.get_or_create(
    nombre="LICENCIATURA EN INCLUSIÓN EDUCATIVA",
    codigo="LIE",
    plan=2023,
    numero_semestres=8
)
print(f"✅ Licenciatura: {lic}")

# Crear materias de ejemplo - USAR get_or_create CON código explícito
materias_data = [
    {"codigo": "LIE2301", "nombre": "Fundamentos de Educación Inclusiva", "semestre": 1},
    {"codigo": "LIE2302", "nombre": "Psicología del Desarrollo", "semestre": 1},
    {"codigo": "LIE2303", "nombre": "Tecnologías para la Inclusión", "semestre": 2},
]

for data in materias_data:
    materia, created = Materia.objects.get_or_create(
        licenciatura=lic,
        codigo=data["codigo"],  # Especificar código explícitamente
        defaults={
            "nombre": data["nombre"],
            "semestre": data["semestre"],
            "creditos": 8
        }
    )
    if created:
        print(f"✅ Materia creada: {materia.codigo} - {materia.nombre}")
    else:
        print(f"⚠️ Materia ya existía: {materia.codigo} - {materia.nombre}")

# Crear alumno de prueba
alumno, created = Alumno.objects.get_or_create(
    matricula="LIE2023001",
    defaults={
        "nombre": "Juan Pérez García",
        "curp": "PEGJ930101HDFRRR01",
        "rfc": "PEGJ930101XXX",
        "licenciatura": "LICENCIATURA EN INCLUSIÓN EDUCATIVA",
        "semestre_actual": 1,
        "email_institucional": "juan.perez@benune.edu.mx",
        "email_personal": "juan@gmail.com",
        "telefono": "5567891234"
    }
)
if created:
    print(f"✅ Alumno creado: {alumno}")
else:
    print(f"⚠️ Alumno ya existía: {alumno}")

# Crear usuario de prueba (Control Escolar)
try:
    usuario, created = Usuario.objects.get_or_create(
        email="control@benune.edu.mx",
        defaults={
            "first_name": "Ana",
            "last_name": "García",
            "tipo_usuario": "control_escolar",
            "turno": "matutino",
            "telefono": "5512345678"
        }
    )
    if created:
        usuario.set_password("password123")  # Contraseña simple para pruebas
        usuario.save()
        print(f"✅ Usuario creado: {usuario}")
    else:
        print(f"⚠️ Usuario ya existía: {usuario}")
except Exception as e:
    print(f"❌ Error creando usuario: {e}")

print("🎉 ¡Datos iniciales creados exitosamente!")