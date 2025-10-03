# create_test_users_fixed.py
import os
import sys
import django
import random
import string

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from usuarios.models import Usuario
from core.encryption import encryption_manager

def create_test_users_no_encryption():
    """Crear usuarios sin cifrar el email para que funcionen con autenticación"""
    
    # Desactivar temporalmente el cifrado para el campo email
    original_encrypt = encryption_manager.encrypt
    original_decrypt = encryption_manager.decrypt
    
    # Función que no cifra para emails
    def no_encrypt_email(data):
        if data is None:
            return None
        return str(data)
    
    # Reemplazar temporalmente los métodos de cifrado
    encryption_manager.encrypt = no_encrypt_email
    encryption_manager.decrypt = lambda x: x  # No descifrar
    
    try:
        # Crear usuario Directivo
        try:
            directivo = Usuario.objects.get(email='directivo@benune.edu.mx')
            print(f"ℹ️  Usuario Directivo ya existe: directivo@benune.edu.mx")
        except Usuario.DoesNotExist:
            directivo = Usuario(
                email='directivo@benune.edu.mx',
                first_name='Juan',
                last_name='Pérez',
                tipo_usuario='directivo',
                is_staff=True,
                is_superuser=False
            )
            directivo.username = 'directivo_admin'
            directivo.set_password('Directivo123')
            directivo.save()
            print(f"✅ Usuario Directivo creado: directivo@benune.edu.mx / Directivo123")
        
        # Crear usuario Control Escolar
        try:
            control_escolar = Usuario.objects.get(email='control@benune.edu.mx')
            print(f"ℹ️  Usuario Control Escolar ya existe: control@benune.edu.mx")
        except Usuario.DoesNotExist:
            control_escolar = Usuario(
                email='control@benune.edu.mx',
                first_name='María',
                last_name='García',
                tipo_usuario='control_escolar',
                is_staff=True,
                is_superuser=False
            )
            control_escolar.username = 'control_admin'
            control_escolar.set_password('Control123')
            control_escolar.save()
            print(f"✅ Usuario Control Escolar creado: control@benune.edu.mx / Control123")
        
        # Crear usuario Docente
        try:
            docente = Usuario.objects.get(email='docente@benune.edu.mx')
            print(f"ℹ️  Usuario Docente ya existe: docente@benune.edu.mx")
        except Usuario.DoesNotExist:
            docente = Usuario(
                email='docente@benune.edu.mx',
                first_name='Carlos',
                last_name='López',
                tipo_usuario='docente',
                is_staff=False,
                is_superuser=False
            )
            docente.username = 'docente_user'
            docente.set_password('Docente123')
            docente.save()
            print(f"✅ Usuario Docente creado: docente@benune.edu.mx / Docente123")
        
        # Crear usuario Alumno
        try:
            alumno = Usuario.objects.get(email='alumno@benune.edu.mx')
            print(f"ℹ️  Usuario Alumno ya existe: alumno@benune.edu.mx")
        except Usuario.DoesNotExist:
            alumno = Usuario(
                email='alumno@benune.edu.mx',
                first_name='Ana',
                last_name='Rodríguez',
                tipo_usuario='alumno',
                is_staff=False,
                is_superuser=False
            )
            alumno.username = 'alumno_user'
            alumno.set_password('Alumno123')
            alumno.save()
            print(f"✅ Usuario Alumno creado: alumno@benune.edu.mx / Alumno123")
            
    finally:
        # Restaurar los métodos originales de cifrado
        encryption_manager.encrypt = original_encrypt
        encryption_manager.decrypt = original_decrypt

if __name__ == '__main__':
    print("🧪 Creando usuarios de prueba (sin cifrado de email)...")
    create_test_users_no_encryption()
    print("🎉 Usuarios creados exitosamente!")
    print("\n🔐 Credenciales de acceso:")
    print("   Directivo: directivo@benune.edu.mx / Directivo123")
    print("   Control Escolar: control@benune.edu.mx / Control123")
    print("   Docente: docente@benune.edu.mx / Docente123")
    print("   Alumno: alumno@benune.edu.mx / Alumno123")