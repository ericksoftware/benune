import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario
from alumnos.models import Alumno

def check_email_status():
    print("=== VERIFICANDO ESTADO DE EMAILS ===")
    
    print("\n--- USUARIOS DEL PERSONAL ---")
    for usuario in Usuario.objects.all():
        email = usuario.email
        is_encrypted = email.startswith('gAAAA') if email else False
        print(f"Email: {email}")
        print(f"Cifrado: {is_encrypted}")
        print(f"Tipo usuario: {usuario.tipo_usuario}")
        print("---")
    
    print("\n--- ALUMNOS ---")
    for alumno in Alumno.objects.all():
        email = alumno.email_institucional
        is_encrypted = email.startswith('gAAAA') if email else False
        print(f"Email: {email}")
        print(f"Cifrado: {is_encrypted}")
        print(f"Alumno: {alumno.nombre_completo()}")
        print("---")

if __name__ == '__main__':
    check_email_status()