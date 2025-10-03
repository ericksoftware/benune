# create_data.py
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from evaluaciones.models import Licenciatura, Materia, Unidad
from usuarios.models import Usuario

def main():
    print("Creando datos iniciales de prueba...")
    
    # Crear licenciatura
    lic, created = Licenciatura.objects.get_or_create(
        nombre="LICENCIATURA EN INCLUSIÓN EDUCATIVA",
        defaults={
            "codigo": "LIE",
            "plan": 2023,
            "numero_semestres": 8
        }
    )
    if created:
        print(f"✓ Licenciatura creada: {lic.nombre}")
        
        # Crear unidades automáticamente para la licenciatura
        unidades_base = [
            (1, 'Unidad Principal'),
            (2, 'Unidad Avanzada'),
        ]
        
        for num, nombre in unidades_base:
            unidad = Unidad.objects.create(
                licenciatura=lic,
                numero=num,
                nombre=nombre
            )
            print(f"  - Unidad creada: {unidad.codigo}")
    else:
        print(f"Licenciatura ya existía: {lic.nombre}")
    
    # Crear materias de ejemplo (actualizado con unidades)
    materias_data = [
        {"codigo": "LIE2301", "nombre": "Fundamentos de Educación Inclusiva", "semestre": 1},
        {"codigo": "LIE2302", "nombre": "Psicología del Desarrollo", "semestre": 1},
        {"codigo": "LIE2303", "nombre": "Tecnologías para la Inclusión", "semestre": 2},
    ]
    
    for data in materias_data:
        # Obtener la primera unidad de la licenciatura
        unidad = Unidad.objects.filter(licenciatura=lic).first()
        
        if unidad:
            materia, created = Materia.objects.get_or_create(
                licenciatura=lic,
                codigo=data["codigo"],
                defaults={
                    "nombre": data["nombre"],
                    "semestre": data["semestre"],
                    "creditos": 8,
                    "unidad": unidad
                }
            )
            if created:
                print(f"✓ Materia creada: {materia.codigo} - {materia.nombre}")
            else:
                print(f"Materia ya existía: {materia.codigo} - {materia.nombre}")
    
    # Crear alumno de prueba
    alumno, created = Alumno.objects.get_or_create(
        matricula="LIE2023001",
        defaults={
            "nombre": "Juan",
            "apellido_paterno": "Perez",
            "apellido_materno": "Garcia",
            "curp": "PEGJ930101HDFRRR01",
            "rfc": "PEGJ930101XXX",
            "licenciatura": "LICENCIATURA EN INCLUSIÓN EDUCATIVA",
            "semestre_actual": 1,
            "email_institucional": "juan.perez@benune.edu.mx",
            "email_personal": "juan@gmail.com",
            "telefono": "5567891234",
            "municipio_nacimiento": "Mexicali",
            "sexo": "hombre",
            "institucion_procedencia": "Preparatoria Estatal",
            "turno": "matutino",
            "plan": 2023
        }
    )
    if created:
        print(f"✓ Alumno creado: {alumno.nombre_completo()} - {alumno.matricula}")
    else:
        print(f"Alumno ya existía: {alumno.nombre_completo()}")
    
    # Crear usuario de Control Escolar
    try:
        usuario, created = Usuario.objects.get_or_create(
            email="control@benune.edu.mx",
            defaults={
                "first_name": "Ana",
                "last_name": "Garcia",
                "tipo_usuario": "control_escolar",
                "turno": "matutino",
                "telefono": "5512345678",
                "is_staff": True,
                "is_active": True
            }
        )
        if created:
            usuario.set_password("password123")
            usuario.save()
            print(f"✓ Usuario Control Escolar creado:")
            print(f"  Email: control@benune.edu.mx")
            print(f"  Contraseña: password123")
            print(f"  Tipo: {usuario.get_tipo_usuario_display()}")
            print(f"  Nombre: {usuario.get_full_name()}")
        else:
            print(f"Usuario ya existía: {usuario.email}")
            # Actualizar contraseña por si acaso
            usuario.set_password("password123")
            usuario.save()
            print(f"  Contraseña actualizada: password123")
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
    
    # Crear usuario Docente de prueba también
    try:
        docente, created = Usuario.objects.get_or_create(
            email="docente@benune.edu.mx",
            defaults={
                "first_name": "Carlos",
                "last_name": "Lopez",
                "tipo_usuario": "docente",
                "turno": "matutino",
                "telefono": "5512345679",
                "is_staff": False,
                "is_active": True
            }
        )
        if created:
            docente.set_password("password123")
            docente.save()
            print(f"✓ Usuario Docente creado:")
            print(f"  Email: docente@benune.edu.mx")
            print(f"  Contraseña: password123")
            print(f"  Tipo: {docente.get_tipo_usuario_display()}")
        else:
            print(f"Usuario docente ya existía: {docente.email}")
            
    except Exception as e:
        print(f"❌ Error creando usuario docente: {e}")
    
    print("\n" + "="*50)
    print("DATOS DE ACCESO PARA PRUEBAS:")
    print("="*50)
    print("CONTROL ESCOLAR:")
    print("  Email: control@benune.edu.mx")
    print("  Contraseña: password123")
    print("  Permisos: Acceso completo al sistema")
    print("\nDOCENTE:")
    print("  Email: docente@benune.edu.mx") 
    print("  Contraseña: password123")
    print("  Permisos: Solo ver información")
    print("\nALUMNO DE PRUEBA:")
    print(f"  Matrícula: {alumno.matricula}")
    print(f"  Nombre: {alumno.nombre_completo()}")
    print("="*50)

if __name__ == "__main__":
    main()