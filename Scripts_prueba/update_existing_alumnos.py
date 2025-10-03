# update_existing_alumnos.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from core.encryption import encryption_manager

def update_existing_alumnos():
    """Actualizar alumnos existentes para asegurar que los datos estén cifrados correctamente"""
    alumnos = Alumno.objects.all()
    
    for alumno in alumnos:
        try:
            # Verificar y actualizar cada campo cifrado si es necesario
            update_fields = []
            
            # Si el CURP parece estar cifrado (largo y con caracteres especiales), no hacer nada
            # Si parece estar en texto plano, cifrarlo
            if alumno.curp and len(alumno.curp) < 100 and not alumno.curp.startswith('gAAAAA'):
                alumno.curp = encryption_manager.encrypt(alumno.curp)
                update_fields.append('curp')
            
            if alumno.nombre and len(alumno.nombre) < 100 and not alumno.nombre.startswith('gAAAAA'):
                alumno.nombre = encryption_manager.encrypt(alumno.nombre)
                update_fields.append('nombre')
            
            if alumno.apellido_paterno and len(alumno.apellido_paterno) < 100 and not alumno.apellido_paterno.startswith('gAAAAA'):
                alumno.apellido_paterno = encryption_manager.encrypt(alumno.apellido_paterno)
                update_fields.append('apellido_paterno')
            
            if alumno.apellido_materno and len(alumno.apellido_materno) < 100 and not alumno.apellido_materno.startswith('gAAAAA'):
                alumno.apellido_materno = encryption_manager.encrypt(alumno.apellido_materno)
                update_fields.append('apellido_materno')
            
            if update_fields:
                alumno.save(update_fields=update_fields)
                print(f"Actualizado: {alumno.matricula} - Campos: {', '.join(update_fields)}")
            else:
                print(f"OK: {alumno.matricula} - Datos ya cifrados")
                
        except Exception as e:
            print(f"Error con alumno {alumno.matricula}: {e}")

if __name__ == "__main__":
    update_existing_alumnos()